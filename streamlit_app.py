from dotenv import load_dotenv, find_dotenv
import streamlit as st

from src.networking.aci.instructions.aci_instructions import INSTRUCTIONS
from src.llm_api.utils.functions import (get_bd_function,
                                         get_tenant_function,
                                         get_fabric_health_function,
                                         build_bd_function,
                                         get_configuration_guideline_function)
from src.networking.aci.base_client import BaseACIClient
from src.streamlit_app.utils.initialize import initialize_app
import pandas as pd
from src.networking.device_manager import create_device_form, save_devices, load_devices, upload_csv
from src.streamlit_app.utils.components import select_models, openai_model_expander
from src.llm_api.openai_api import Conversation
from loguru import logger
from src.settings import get_settings

SETTINGS = get_settings()

_ = load_dotenv((find_dotenv()))


st.set_page_config(page_title="Personal Intelligent Networking Guru (PING)")


if 'initialized' not in st.session_state:
    initialize_app()

session_state = st.session_state

# Sidebar configuration
with st.sidebar:
    st.header("Personal Intelligent Networking Guru (PING)")
    st.markdown(f"""# <span style=color:#2E9BF5><font size=3>{SETTINGS.version}</font></span>""",
                unsafe_allow_html=True)
    select_models()
    if 'OpenAI' in session_state.selected_model:
        openai_model_expander()

# chat page

st.markdown("""Quick start guide:
1. enter device information
2. start chatting
""")

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

clicked_example_query = None
for _ in range(5):
    st.write("")
for i, (btn_col, example_query) in enumerate(zip(st.columns(3), session_state.example_queries)):
    with btn_col:
        if st.button(example_query, key=f"query{i}"):
            clicked_example_query = example_query


if 'openai_api_key' in st.session_state:
    openai_api_key = st.session_state.openai_api_key

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    aci_functions = [get_fabric_health_function, get_bd_function, build_bd_function, get_tenant_function,
                     get_configuration_guideline_function]

    conversation = Conversation(
        api_key=openai_api_key,
        max_retries=SETTINGS.llm_api_max_retry,
        timeout=60,
        temperature=SETTINGS.llm_temperature,
        system_prompt=f"{INSTRUCTIONS}",
        model=SETTINGS.openai_model,
        functions=aci_functions
    )
    # React to user input
    if prompt := st.chat_input("What are we engineering today?"):
        # Add user message to chat history
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Generate response
        context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        conversation.add_user_message(prompt)
        with st.spinner("thinking hard....."):
            conversation.send_completion_request()
            if conversation.response.get('tool_calls'):
                logger.bind(log="chat").info("Making function call.... ",
                                             conversation.response['tool_calls'][0]['function'])
                apic = st.session_state.devices[0]['ip']
                apic_username = st.session_state.devices[0]['username']
                apic_password = st.session_state.devices[0]['password']
                aci_client = BaseACIClient(apic=apic, apic_username=apic_username, apic_password=apic_password)
                aci_client.initiate_rest()
                function_result = conversation.call_function(aci_client)
                conversation.send_completion_request()
            response = conversation.messages[-1].get('content')

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

else:
    st.warning("API key not found. Please make sure you've entered your API key in the sidebar.")


# React to user input
# if prompt := st.chat_input("What is your message?"):
#     # Display user message in chat message container
#     st.chat_message("user").markdown(prompt)
#     # Add user message to chat history
#     st.session_state.messages.append({"role": "user", "content": prompt})
#
#     # Here you would normally generate a response from your AI model
#     # For this example, we'll just echo the user's message
#     response = f"Echo: {prompt}"
#
#     # Display assistant response in chat message container
#     with st.chat_message("assistant"):
#         st.markdown(response)
#     # Add assistant response to chat history
#     st.session_state.messages.append({"role": "assistant", "content": response})

    # Settings

    # with st.expander("Settings", expanded=False):
    #     if is_community_key:
    #         model_options = [MODEL_NAME]  # show only 3.5 if community key
    #         index = 0
    #     else:
    #         model_options = ALLOWED_MODELS  # guaranteed to include MODEL_NAME
    #         index = model_options.index(chat_state.bot_settings.llm_model_name)
    #     # TODO: adjust context length (for now assume 16k)
    #     chat_state.bot_settings.llm_model_name = st.selectbox(
    #         "Language model", model_options, disabled=is_community_key, index=index
    #     )
    #
    #     # Temperature
    #     chat_state.bot_settings.temperature = st.slider(
    #         "Temperature",
    #         min_value=0.0,
    #         max_value=2.0,
    #         value=TEMPERATURE,
    #         step=0.1,
    #         format="%f",
    #     )
    #     if chat_state.bot_settings.temperature >= 1.5:
    #         st.caption(":red[Very high temperatures can lead to **jibberish**]")
    #     elif chat_state.bot_settings.temperature >= 1.0:
    #         st.caption(":orange[Consider a lower temperature if precision is needed]")

    # Resources

    # with st.expander("Resources", expanded=True):
    #     "[Command Cheatsheet](https://github.com/reasonmethis/docdocgo-core/blob/main/README.md#using-docdocgo)"
    #     "[Full Docs](https://github.com/reasonmethis/docdocgo-core/blob/main/README.md)"


# if __name__ == "__main__":#
#     while True:
#         prompt = input("\nHow can I assist you today? => ")
#         if not prompt:
#             sys.exit("no prompts entered, exiting....")
#
#         # if chatGPT responded with a function name we'll call the function mentioned
#         print("\n==Response==\n")
#
#         if conversation.response.get('tool_calls'):
#             LOGGER.info("Making function call.... ", conversation.response['tool_calls'][0]['function'])
#             aci_client = BaseACIClient()
#             aci_client.initiate_rest()
#             function_result = conversation.call_function(aci_client)
#             response = conversation.send_completion_request()
#             print(response.get('content'))
#         else:
#             print(conversation.response.get('content'))
#
#         print("\n==End of response==")
