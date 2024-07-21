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
        hostname = st.text_input("Hostname")
        username = st.text_input("Username")
        password = encode_password(st.text_input("Password", type="password"))
        os = st.selectbox("Operating System", ["IOS-XE", "NX-OS", "APIC"])
        submitted = st.form_submit_button("Add Device")
        if submitted:
            return {"ip": ip, "hostname": hostname, "username": username, "password": password, "os": os}
    return None


def get_device_login(hostname="", device_ip=""):
    for device in st.session_state.devices:
        if hostname.upper() in device.values() or device_ip in device.values():
            return device['ip'], device['username'], decode_password(device['password'])
    else:
        print (f"host name {hostname} not found")
        return st.session_state.messages.append(f"invalid hostname {hostname}")


def upload_csv():
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        if set(data.columns) == {"ip", "username", "password", "os"}:
            st.session_state.devices = data.to_dict('records')
            st.success("Devices loaded successfully!")
        else:
            st.error("CSV file must contain columns: ip, username, password, os")
