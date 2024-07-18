import json
import streamlit as st
import base64
import pandas as pd


class DeviceManager:
    pass


def encode_password(password):
    return base64.b64encode(password.encode()).decode()


def decode_password(encoded):
    return base64.b64decode(encoded.encode()).decode()


def save_devices():
    with open('devices.json', 'w') as f:
        json.dump(st.session_state.devices, f)


def load_devices():
    try:
        with open('devices.json', 'r') as f:
            st.session_state.devices = json.load(f)
    except FileNotFoundError:
        st.session_state.devices = []


def create_device_form():
    with st.form("device_info_form"):
        st.write("Enter Device Information")
        ip = st.text_input("IP Address")
        username = st.text_input("Username")
        password = encode_password(st.text_input("Password", type="password"))
        os = st.selectbox("Operating System", ["IOS", "IOS-XE", "NX-OS", "APIC"])
        submitted = st.form_submit_button("Add Device")
        if submitted:
            return {"ip": ip, "username": username, "password": password, "os": os}
    return None


def upload_csv():
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        if set(data.columns) == {"ip", "username", "password", "os"}:
            st.session_state.devices = data.to_dict('records')
            st.success("Devices loaded successfully!")
        else:
            st.error("CSV file must contain columns: ip, username, password, os")