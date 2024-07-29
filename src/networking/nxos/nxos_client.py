import os
from src.networking.nxos.nxsession import Session
from loguru import logger
import streamlit as st
from src.networking.device_manager import get_device_login
from dotenv import load_dotenv
load_dotenv()


def get_or_create_nxos_device_session(device_name):
    session_key = f"device_session_{device_name}"
    if session_key not in st.session_state:
        ip, username, password, api_port = get_device_login(device_name)
        st.session_state[session_key] = BaseClient(ip, username, password, api_port)
    return st.session_state[session_key]


class BaseClient:
    """
    This class is for interacting with the NX-OS devices via either API or SSH
    """

    def __init__(self, device_ip, username, password, api_port=443):
        self.device_ip = device_ip
        self.username = username
        self.password = password
        self.api_port = api_port
        self.rest_session = None
        self.cli_session = Session(f"https://{self.device_ip}:{self.api_port}", uid=f"{self.username}",
                                   pwd=f"{self.password}")
        self.cli_session.login()

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
        try:
            if ";" in cmd:
                for result in cli_result:
                    if result['code'] != '200':
                        logger.bind(log="chat").error(f"{result['clierror']}, {cmd}")
                        return
                else:
                    return f"all changes {cmd} executed successfully"
            if cli_result['output'] != '200':
                logger.bind(log="chat").error(f"{cli_result['clierror']}, {cmd}")
                return
            return f"all changes {cmd} executed successfully"
        except KeyError as e:
            return f"Error executing the CLI commands {e}, see logs for details"


def reset_demo_topology():
    r1_ip, username, password, r1_api_port = get_device_login("R1")
    r1_session = BaseClient(r1_ip, username, password, r1_api_port)

    r2_ip, username, password, r2_api_port = get_device_login("R2")
    r2_session = BaseClient(r2_ip, username, password, r2_api_port)

    # r1 has no mtu settings and no ospf network point-to-point, vlan10 interface missing ip router ospf a 0
    r1_cmd = """
    default interface eth1/1 ; default interface vlan10 ; 
    interface Ethernet1/1 ; no switchport ; 
    ip address 10.0.12.1/24 ; ip router ospf 1 area 0.0.0.0 ; no shutdown ;
    interface vlan10 ; no shut ; ip address 10.1.10.254/24 ; 
    """
    r1_session.config_cmd(r1_cmd)

    r2_cmd = """
    default interface eth1/1 ; default interface vlan20 ; 
    interface eth1/1 ; no switchport ; mtu 9216 ; ip address 10.0.12.2/24 ; 
    ip ospf network point-to-point ;
    ip router ospf 1 area 0.0.0.2 ;
    shutdown ;
    interface vlan20 ; no shut ; ip address 10.1.20.254/24 ;
    """
    r2_session.config_cmd(r2_cmd)