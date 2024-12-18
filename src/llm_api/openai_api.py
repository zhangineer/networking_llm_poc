from openai import OpenAI
from typing import List
import json
from src.llm_api.utils.helper import FUNCTION_REGISTRY
import tiktoken
from loguru import logger
import streamlit as st

encoding_model_messages = "gpt-4o"
encoding_model_strings = "cl100k_base"
function_call_limit = 50

# TODO - handle quota error
'''openai.RateLimitError: Error code: 429 - {'error': {'message': 'You exceeded your current quota, 
please check your plan and billing details. For more information on this error, read the docs: 
https://platform.openai.com/docs/guides/error-codes/api-errors.', 
'type': 'insufficient_quota', 'param': None, 'code': 'insufficient_quota'}}'''


class Conversation:
    def __init__(self,
                 api_key: str,
                 max_retries: int,
                 timeout: int,
                 temperature: float,
                 system_prompt: str,
                 model: str = "gpt-4o", # update so models are loaded dynamically
                 tool_choice: str = "auto",
                 max_tokens=4096,
                 functions: List = None):
        self.client = OpenAI(api_key=api_key, timeout=timeout, max_retries=max_retries)
        self.system_prompt = system_prompt
        if not st.session_state.messages:
            self.add_sys_prompt()
        self.model = model
        self.functions = functions
        self.tool_choice = tool_choice
        self.usage = {}
        self.response = {}
        self.max_tokens = max_tokens
        self.temperature = temperature

    def add_sys_prompt(self):
        return st.session_state.messages.append({"role": "system", "content": self.system_prompt})

    @staticmethod
    def add_user_message(message):
        return st.session_state.messages.append({"role": "user", "content": message})

    @staticmethod
    def add_function_call_to_messages(function_name, function_call_result, tool_call_id):
        return st.session_state.messages.append(
            {
                "tool_call_id": tool_call_id,
                "role": "tool",
                "name": function_name,
                "content": function_call_result,
            }
        )

    def send_completion_request(self):
        logger.bind(log="chat").info(
            f"Sending completion request to chatGPT with the following:\n "
            f"Message: {st.session_state.messages}\n"
            f"Model: {self.model}\n"
            f"Tools: {self.functions}\n"
            f"ToolChoice: {self.tool_choice}\n"
        )
        try:
            res = self.client.chat.completions.create(
                model=self.model,
                messages=st.session_state.messages,
                tools=self.functions,
                tool_choice=self.tool_choice,
                temperature=self.temperature,
                top_p=0,
                max_tokens=self.max_tokens
            )
            # if not res:
            #     logger.bind(log="chat").error(f"chatGPT did not return any response")
            #     st.error("chatGPT did not return any response")
            self.usage = res.usage.model_dump()
            self.response = res.choices[0].message.model_dump()  # Returns dictionary
            if not self.response.get('function_call'):
                self.response.pop('function_call')
            logger.bind(log="chat").info(f"chatGPT responded: {self.response}")
            # each time we get a response back, we need to add the message to the context
            st.session_state.messages.append(self.response)
            return self.response
        except Exception as e:
            print ("HIT AN ESCEPTION !!! BAD REQUEST", e)
            st.error(e)

    def call_function(self):
        """
        Call the function returned by chatGPT. A list of functions is found in the FUNCTION_REGISTRY
        Args:
            instance_name: instance of client.
                            This is instantiated by creating a Session object in the case with ACI

        Returns: Returns the result of the function call.

        We can choose to pass the function call results directly back to OpenAI which it will
        interpret the message for us and provide a human-readable text ( however, the response structure can be inconsistent)

        Otherwise, we raise KeyError
        """
        print("Function to call", self.response['tool_calls'])
        function_call_results = []
        for tool_call in self.response["tool_calls"]:
            function_name = tool_call["function"]["name"]
            kwargs = json.loads(tool_call["function"]["arguments"])
            logger.bind(log="chat").info(f"Calling function: \"{function_name}\" with arguments \"{kwargs}\"")
            tool_call_id = tool_call['id']
            # if function_name == 'get_configuration_guideline':
            #     function_call_result = get_configuration_guideline(query=kwargs["query"])
            if function_name in FUNCTION_REGISTRY:
                # dynamically call function - matching function call name to what's stored in the FUNCTION_REGISTRY
                function_call_result = FUNCTION_REGISTRY[function_name](**kwargs)
                function_call_results.append(function_call_result)
                logger.bind(log="chat").info(f"function call result {function_call_result}")
                print(f"Function call returned this result: {function_call_result}")
                self.add_function_call_to_messages(function_name=function_name,
                                                   function_call_result=function_call_result,
                                                   tool_call_id=tool_call_id)
            else:
                logger.bind(log="chat").error(f"Function '{function_name}' not found in function registry {FUNCTION_REGISTRY}")
                raise KeyError(f"Function '{function_name}' not found in function registry {FUNCTION_REGISTRY}")
        return function_call_results

    @staticmethod
    def num_tokens_from_messages():
        """Returns the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(encoding_model_messages)
        except KeyError:
            encoding = tiktoken.get_encoding(encoding_model_strings)

        num_tokens = 0
        for message in st.session_state.messages:
            num_tokens += 4
            for key, value in message.items():
                num_tokens += len(encoding.encode(str(value)))
                if key == "name":
                    num_tokens += -1
        num_tokens += 2
        return num_tokens