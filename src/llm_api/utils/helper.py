"""

General Utility Functions

"""
from src.networking.nxos.nxos_client import get_or_create_nxos_device_session
FUNCTION_REGISTRY = {}


def register(func):
    """
    This decorator is used to dynamically build a dictionary called FUNCTION_REGISTRY to
    map function names to actual functions
    """
    FUNCTION_REGISTRY[func.__name__] = func
    return func


@register
def execute_show_cmd(device_name, cmd):
    # Get or create the session
    session = get_or_create_nxos_device_session(device_name)
    # Execute the command
    result = session.show_cmd(cmd)
    return result


@register
def execute_config_cmd(device_name, cmd):
    # Get or create the session
    session = get_or_create_nxos_device_session(device_name)
    # Execute the command
    result = session.config_cmd(cmd)
    return result


def create_function_config(name: str, description: str, properties: dict = None, required: list = None) -> dict:
    """
    Args:
        name: Name of the function for OpenAI to call
        description: Description of the function.
        properties: A dictionary defining the properties of the parameters.
        required: A list of required properties.

    Returns:
        OpenAI Specific dictionary format for the definition of a function


    create an OpenAI specific dictionary format, example:

    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "format": {
                        "type": "string",
                        "enum": [
                            "celsius",
                            "fahrenheit"
                        ],
                        "description": "The temperature unit to use. Infer this from the users location."
                    }
                },
                "required": [
                    "location",
                    "format"
                ]
            }
        }
    }
    """

    if properties is None:
        properties = {}

    if required is None:
        required = []

    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
    }
