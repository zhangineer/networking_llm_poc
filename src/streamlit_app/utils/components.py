import streamlit as st


def update_model():
    st.session_state.selected_model = f"model: {st.session_state.model_selector}"
    st.session_state.selected_model_expanded = False


def select_models():
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = "OpenAI ChatGPT"
        st.session_state.selected_model_expanded = True
    models = ["OpenAI ChatGPT", "llama3"]  # "Claude Sonnet", "LLAMA3", "Mistral 7B" add in the future
    public_models = ["OpenAI ChatGPT", "Claude Sonnet"]  # List of models that trigger a warning

    with st.expander(st.session_state.selected_model, expanded=st.session_state.selected_model_expanded):
        selected_model = st.selectbox(
            "Choose the model you want to use:",
            models,
            key="model_selector",
            on_change=update_model
        )
        if selected_model in public_models:
            st.warning(f"⚠️ {selected_model} is a public model. Use with caution.")
    return selected_model


def openai_model_expander():
    if 'OpenAI' in st.session_state.selected_model:
        with st.expander("OpenAI API Key", expanded=True):
            supplied_openai_api_key = st.text_input(
                "OpenAI API Key",
                label_visibility="collapsed",
                key="openai_api_key",
                type="password",
            )
            if not supplied_openai_api_key:
                st.warning("No API key provided, using the community key (restricted usage)")
                # st.error("You must supply an API key before using chat")
                # is_community_key = not BYPASS_SETTINGS_RESTRICTIONS

            else:
                # Use the key entered by the user as the OpenAI API key
                st.session_state.api_key = supplied_openai_api_key
