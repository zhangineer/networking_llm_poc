import os

from nxsession import Session
from dotenv import load_dotenv, find_dotenv

load_dotenv((find_dotenv()))


class BaseACIClient:
    """
    This class is for interacting with the NX-OS devices via SSH
    """

    def __init__(self, device_ip, username, password):
        self.device_ip = device_ip
        self.username = username
        self.password = password
        self.api_port = os.getenv('api_port', 443)
        self.rest_session = None
        self.url = f"https://{device_ip}"

    def initiate_rest(self):
        self.rest_session = Session(f"https://{self.device_ip}:{self.api_port}", uid=f"{self.username}",
                                    pwd=f"{self.password}")
        self.rest_session.login()

# class ShowCmds(BaseACIClient):
#     def show_version(self):
#         result = self.rest_session.
#
#     def response(self):
#         return self.rest_session.get()


nx_session = Session(url='https://10.100.100.1', uid='admin', pwd='WWTwwt1!')
login = nx_session.login()
result = nx_session.push_to_device(data={
          "ins_api": {
            "version": "1.0",
            "type": "cli_show",
            "chunk": "0",
            "sid": "sid",
            "input": "show bgp l2vpn evpn",
            "output_format": "json"
          }
        }
   )
print (result.text)