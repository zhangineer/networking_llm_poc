import tiktoken
import json
import os
import sys
from dotenv import load_dotenv, find_dotenv
from typing import List
from openai import OpenAI

from app.logger_config import create_logger
from app.aci.aci_instructions import INSTRUCTIONS
from app.functions import (get_bd_function,
                           get_tenant_function,
                           get_fabric_health_function,
                           build_bd_function,
                           get_configuration_guideline_function)
from app.aci.base_client import BaseACIClient
from app.utils import FUNCTION_REGISTRY
from app.aci.rag import get_configuration_guideline

LOGGER = create_logger('app.log', __name__)

_ = load_dotenv((find_dotenv()))


llm_model = "gpt-4-0613"
llm_max_tokens = 8192
llm_system_prompt = f"{INSTRUCTIONS}"
encoding_model_messages = "gpt-4-0613"
encoding_model_strings = "cl100k_base"
function_call_limit = 10


class Conversation:
    def __init__(self, system_prompt: str, model: str = "gpt-4-0613", tool_choice: str ="auto", max_tokens=256,
                 functions: List = None, temperature: float = 0):
        self.client = OpenAI(
            # This is the default and can be omitted
            api_key=os.environ.get("OPENAI_API_KEY")
        )
        self.system_prompt = system_prompt
        self.messages = []
        self.model = model
        self.functions = functions
        self.tool_choice = tool_choice
        if system_prompt:
            self.add_sys_prompt()
        self.usage = {}
        self.response = {}
        self.max_tokens = max_tokens
        self.temperature = temperature

    def add_sys_prompt(self):
        return self.messages.append({"role": "system", "content": self.system_prompt})

    def add_user_message(self, message):
        return self.messages.append({"role": "user", "content": message})

    def send_completion_request(self):
        LOGGER.info(
            f"Sending completion request to chatGPT with the following:\n "
            f"Message: {json.dumps(self.messages, indent=4)}\n"
            f"Model: {self.model}\n"
            f"Tools: {self.functions}\n"
            f"ToolChoice: {self.tool_choice}\n"
        )
        res = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.functions,
            tool_choice=self.tool_choice,
            temperature=self.temperature,
            top_p=0,
            max_tokens=self.max_tokens
        )
        self.usage = res.usage.model_dump()
        self.response = res.choices[0].message.model_dump()  # Returns dictionary
        if not self.response.get('function_call'):
            self.response.pop('function_call')
        LOGGER.info(f"chatGPT responded: {json.dumps(self.response, indent=4)}")
        # each time we get a response back, we need to add the message to the context
        self.messages.append(self.response)
        return self.response

    def call_function(self, instance_name):
        """
        Call the function returned by chatGPT. A list of functions is found in the FUNCTION_REGISTRY
        Args:
            instance_name: instance of ACI client.
                            This is instantiated by creating a Session object in the case with ACI

        Returns: Returns the result of the function call.

        We can choose to pass the function call results directly back to OpenAI which it will
        interpret the message for us and provide a human-readable text ( however, the response structure can be inconsistent)

        Otherwise, we raise KeyError
        """
        function_name = self.response["tool_calls"][0]["function"]["name"]
        kwargs = json.loads(self.response["tool_calls"][0]["function"]["arguments"])
        tool_call_id = self.response["tool_calls"][0]["id"]
        LOGGER.info(f"Calling function: \"{function_name}\" with arguments \"{kwargs}\"")
        if function_name == 'get_configuration_guideline':
            function_call_result = get_configuration_guideline(query=kwargs["query"])
        elif function_name in FUNCTION_REGISTRY:
            # dynamically call function - matching function call name to what's stored in the FUNCTION_REGISTRY
            function_call_result = FUNCTION_REGISTRY[function_name](instance_name, **kwargs)
        else:
            raise KeyError(f"Function '{function_name}' not found in function registry {FUNCTION_REGISTRY}")
        LOGGER.info(f"function call result {json.dumps(function_call_result, indent=4)}")
        self.messages.append(
            {
                "tool_call_id": tool_call_id,
                "role": "tool",
                "name": function_name,
                "content": json.dumps(function_call_result),
            }
        )
        return function_call_result

    def num_tokens_from_messages(self):
        """Returns the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(encoding_model_messages)
        except KeyError:
            encoding = tiktoken.get_encoding(encoding_model_strings)

        num_tokens = 0
        for message in self.messages:
            num_tokens += 4
            for key, value in message.items():
                num_tokens += len(encoding.encode(str(value)))
                if key == "name":
                    num_tokens += -1
        num_tokens += 2
        return num_tokens


def get_dn(data):
    for key in data:
        if 'attributes' in data[key] and 'dn' in data[key]['attributes']:
            return data[key]['attributes']['dn']
    return None


if __name__ == "__main__":
    print(
        "\nHi, I'm an ACI GPT agent, I can provide information for your ACI fabric")
    print(
        "Here are some example prompts:\n"
        "- How is my fabric doing?\n"
        "- Can you get me a list of BDs with UR enabled?\n"
        "- Can you add a new BD named VLAN5_BD to Tenant customerA?\n"
        "- How many BDs are there?\n"
    )

    aci_functions = [get_fabric_health_function, get_bd_function, build_bd_function, get_tenant_function,
                     get_configuration_guideline_function]
    conversation = Conversation(system_prompt=f"{INSTRUCTIONS}", model="gpt-4-0613", functions=aci_functions)
    while True:
        prompt = input("\nHow can I assist you today? => ")
        if not prompt:
            sys.exit("no prompts entered, exiting....")
        conversation.add_user_message(prompt)
        conversation.send_completion_request()

        # if chatGPT responded with a function name we'll call the function mentioned
        print("\n==Response==\n")

        if conversation.response.get('tool_calls'):
            LOGGER.info("Making function call.... ", conversation.response['tool_calls'][0]['function'])
            aci_client = BaseACIClient()
            aci_client.initiate_rest()
            function_result = conversation.call_function(aci_client)
            response = conversation.send_completion_request()
            print(response.get('content'))
        else:
            print(conversation.response.get('content'))

        print("\n==End of response==")
