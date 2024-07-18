import streamlit as st
from src.settings import get_settings
from src.streamlit_app.config import VENDORS_OS_MAPPING
from src.streamlit_app.config import EXAMPLE_PROMPTS

SETTINGS = get_settings()


def initialize_app():
    # set the initial variables for streamlit state
    st.session_state.initialized = True
    st.session_state.openai_api_key = SETTINGS.openai_api_key

    st.session_state.idx_file_upload = -1
    st.session_state.uploader_form_key = "uploader-form"

    st.session_state.idx_file_download = -1
    st.session_state.downloader_form_key = "downloader"

    # st.session_state.user_avatar = USER_AVATAR
    # st.session_state.bot_avatar = CHATBOT_AVATAR

    st.session_state.example_queries = [q.strip() for q in EXAMPLE_PROMPTS.strip().split("\n")]
    st.session_state.default_vendor = list(VENDORS_OS_MAPPING.keys())[0]
