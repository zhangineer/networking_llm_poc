import pickle
from pathlib import Path

from dotenv import load_dotenv, find_dotenv
import streamlit as st

from src.networking.nxos.nxos_instructions import INSTRUCTIONS
from src.networking.nxos.nxos_client import reset_demo_topology
from src.llm_api.utils.functions import (get_bd_function,
                                         get_tenant_function,
                                         get_fabric_health_function,
                                         build_bd_function,
                                         get_configuration_guideline_function)
from src.streamlit_app.utils.initialize import initialize_app
import pandas as pd
from src.networking.device_manager import create_device_form, save_devices, load_devices, upload_csv
from src.streamlit_app.utils.components import select_models, openai_model_expander
from src.llm_api.openai_api import Conversation
from loguru import logger
from src.settings import get_settings
from src.llm_api.utils.functions import (execute_show_cmd_function, execute_config_cmd_function)
import streamlit_authenticator as stauth

SETTINGS = get_settings()

_ = load_dotenv((find_dotenv()))


st.set_page_config(page_title="Personal Intelligent Networking Guru (PING)")

names = ["Peter Parker", "Doctor Strange", "Captain Marvel", "Groot", "Homelander"]
usernames = ["pparker", "drstrange", "cmarvel", "iamgroot", "homelander"]

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names, usernames, hashed_passwords, cookie_name="assistant", key="random-key", cookie_expiry_days=30)
name, authentication_status, username = authenticator.login("Login", "main") # specify the name of the login page, and where it should be located (main or sidebar)


if authentication_status is False:
    st.error("incorrect username or password")

elif authentication_status is None:
    st.warning("please enter username/password")

else:
    if 'initialized' not in st.session_state:
        initialize_app()

    session_state = st.session_state

    # Sidebar configuration
    with st.sidebar:
        authenticator.logout("Logout", "sidebar")
        st.title(f"Welcome {name}")
        st.header("Personal Intelligent Networking Guru (PING)")
        st.markdown(f"""# <span style=color:#2E9BF5><font size=3>{SETTINGS.version}</font></span>""",
                    unsafe_allow_html=True)
        select_models()
        if 'OpenAI' in session_state.selected_model:
            openai_model_expander()

    st.write("Hello Welcome !!")

    assistant_tab, device_tab, topology_tab = st.tabs(["Assistant", "Devices", "Topology"])

    with device_tab:
        # chat page
        st.header("Devices Information")

        upload_csv()
        load_devices()
        expand_form = len(st.session_state.devices) == 0

        with st.expander("Add new devices", expanded=expand_form):
            new_device = create_device_form()
            if new_device:
                if 'devices' not in st.session_state:
                    st.session_state.devices = []
                st.session_state.devices.append(new_device)
                save_devices()
                st.success("Device added successfully!")

        with st.expander("View Loaded Devices", expanded=False):
            if 'devices' in st.session_state and st.session_state.devices:
                # Create a DataFrame with only IP and OS
                df = pd.DataFrame(st.session_state.devices)[['ip', 'os']]

                # Display the DataFrame as a table
                st.table(df)

                # Display the count of devices
                st.write(f"Total devices: {len(st.session_state.devices)}")
            else:
                st.write("No devices loaded.")

    with topology_tab:
        st.header("Topology")
        pass

    with assistant_tab:
        st.header("Chat Assistant")

        clicked_example_query = None
        # for _ in range(5):
        #     st.write("")
        # for i, (btn_col, example_query) in enumerate(zip(st.columns(3), session_state.example_queries)):
        #     with btn_col:
        #         if st.button(example_query, key=f"query{i}"):
        #             clicked_example_query = example_query

        if 'openai_api_key' in st.session_state:
            if "messages" not in st.session_state:
                st.session_state.messages = []

            openai_api_key = st.session_state.openai_api_key

            functions = [execute_show_cmd_function, execute_config_cmd_function]

            if 'conversation' not in st.session_state:
                st.session_state.conversation = Conversation(
                    api_key=openai_api_key,
                    max_retries=SETTINGS.llm_api_max_retry,
                    timeout=60,
                    temperature=SETTINGS.llm_temperature,
                    system_prompt=f"{INSTRUCTIONS}",
                    model=SETTINGS.openai_model,
                    functions=functions
                )
                with st.spinner("resetting demo topology, please standby..."):
                    reset_demo_topology()
            conversation = st.session_state.conversation

            for message in st.session_state.messages[1:]:
                if message.get('content') is not None:
                    with st.chat_message(message["role"]):
                        if message.get("content") and 'tool_call_id' not in message.keys():
                            st.markdown(message["content"])
                        if 'tool_call_id' in message.keys():
                            expander = st.expander("cli command result")
                            expander.code(message['content'], language="plain_text")

            def on_submit():
                conversation.add_user_message(st.session_state.user_message)

            try:
                # React to user input
                if prompt := st.chat_input("What are we engineering today?", key="user_message", on_submit=on_submit):
                    with st.spinner("thinking hard....."):
                        # Send completion request along with user prompt
                        openai_response = conversation.send_completion_request()
                        while openai_response.get('tool_calls'):
                            function_name = openai_response['tool_calls'][0]['function']['name']
                            logger.bind(log="chat").info(f"Making function call.... {function_name}")
                            # if "we want to access apic": #TODO-add-logic
                            #         apic = st.session_state.devices[0]['ip']
                            #         apic_username = st.session_state.devices[0]['username']
                            #         apic_password = st.session_state.devices[0]['password']
                            #         aci_client = BaseACIClient(apic=apic, apic_username=apic_username, apic_password=apic_password)
                            #         aci_client.initiate_rest()
                            #         function_result = conversation.call_function(aci_client)
                            #         conversation.send_completion_request()
                            #     response = conversation.messages[-1].get('content')
                            # elif "we want to access nxos": #TODO-add-logic
                            # nxos_device_ip = st.session_state.devices[1]['ip']
                            # nxos_username = st.session_state.devices[1]['username']
                            # nxos_password = st.session_state.devices[1]['password']
                            # nxos_client = BaseClient(device_ip=nxos_device_ip, username=nxos_username,
                            #                          password=nxos_password)
                            if 'connection_error' in st.session_state and st.session_state.connection_error:
                                st.error(f"Connection Error: {st.session_state.connection_error}")
                            # if calling device login, then we get this: get_device_login\" with arguments \"{'hostname': 'r1'}
                            conversation.call_function()
                            openai_response = conversation.send_completion_request()
                            if openai_response.get("content"):
                                st.markdown(openai_response["content"])
                            # elif function_name == "get_device_login":
                            #     login_fc_result = conversation.call_function()
                            #     print ("current last message received.....", st.session_state.messages[-1])
                            #     print ("after sending the login fc call result...", conversation.send_completion_request()) # trigger openAI to use the username/password to call baseclient
                            #     inst = conversation.call_function(nxos_client)
                            # openai_response = conversation.send_completion_request()
                    st.rerun()

            except Exception as e:
                import traceback
                logger.bind(log="chat").exception(f"unhandled exceptions: \n{traceback.format_exc()}")

                # Display a user-friendly error message
                st.error("An unexpected error occurred. Please try again later or contact support.")

        else:
            st.warning("API key not found. Please make sure you've entered your API key in the sidebar.")