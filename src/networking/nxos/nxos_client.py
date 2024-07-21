import os
from src.networking.nxos.nxsession import Session
from loguru import logger
import streamlit as st
from src.networking.device_manager import get_device_login


def get_or_create_nxos_device_session(device_name):
    session_key = f"device_session_{device_name}"
    if session_key not in st.session_state:
        ip, username, password = get_device_login(device_name)
        st.session_state[session_key] = BaseClient(ip, username, password)
    return st.session_state[session_key]


class BaseClient:
    """
    This class is for interacting with the NX-OS devices via either API or SSH
    """

    def __init__(self, device_ip, username, password):
        self.device_ip = device_ip
        self.username = username
        self.password = password
        self.api_port = os.getenv('api_port', 443)
        self.rest_session = None
        self.cli_session = Session(f"https://{self.device_ip}:{self.api_port}", uid=f"{self.username}",
                                   pwd=f"{self.password}")
        self.cli_session.login()
        self.url = f"https://{device_ip}"

    def initiate_rest(self):
        self.rest_session = Session(f"https://{self.device_ip}:{self.api_port}", uid=f"{self.username}",
                                    pwd=f"{self.password}")
        self.rest_session.login()

    #TODO - add error handling for different status code for when making ins_api call
    def show_cmd(self, cmd):
        # reformat cmd, this is to ensure the formatting when there are multiple commands entered as a single line
        cmd = " ; ".join([c.strip() for c in cmd.split(";")])
        payload = {
          "ins_api": {
            "version": "1.0",
            "type": "cli_show_ascii",
            "chunk": "0",
            "sid": "sid",
            "input": f"{cmd}",
            "output_format": "json"
          }
        }
        cli_result = self.cli_session.push_to_device(payload).json()['ins_api']['outputs']['output']
        logger.bind(log="chat").info(f"CLI command: {cmd} output result.. {cli_result}")
        try:
            if ";" in cmd:  # when running multiple CLI commands in one line, output is a list
                body = ""
                for result in cli_result:
                    if not result['body']:  # if no results
                        body += f"!Command:{result['input']}\n[no output]"
                    else:
                        body += result['body']
                return body
            if not cli_result['body']:
                return f"!Command:{cli_result['input']}\n[no output]"
            return cli_result['body']

        except KeyError as e:
            return f"Error executing the CLI commands {e}, see logs for details"

    def config_cmd(self, cmd):
        cmd = " ; ".join([c.strip() for c in cmd.split(";")])
        payload = {
          "ins_api": {
            "version": "1.0",
            "type": "cli_conf",
            "chunk": "0",
            "sid": "sid",
            "input": f"{cmd}",
            "output_format": "json",
            "rollback": "stop-on-error"
          }
        }
        cli_result = self.cli_session.push_to_device(payload).json()['ins_api']['outputs']['output']
        logger.bind(log="chat").info(f"CLI command: {cmd} output result.. {cli_result}")
        # note that we do not support single command entry for configuration such as only entering "config t"
        try:
            for result in cli_result:
                if result['code'] != '200':
                    logger.bind(log="chat").error(f"{result['clierror']}, {cmd}")
            else:
                return f"all changes {cmd} executed successfully"
        except KeyError as e:
            return f"Error executing the CLI commands {e}, see logs for details"