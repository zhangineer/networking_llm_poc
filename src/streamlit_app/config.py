"""
Store all application internal configurations
"""

# Application version
VERSION = "alpha"

# vendor to OS mapping
VENDORS_OS_MAPPING = {
    "cisco": ["ios-xr", "ios-xe", "nxos", "aci"],
    "arista": ["eos"],
    "juniper": ["junos"],
    "nvidia": ["cumulus", "sonic"]
}

# Chat mode mappings
CHAT_MODES = {
    "default": "normal_chat",
    "creative": "creative_mode",
    "professional": "business_mode",
}

CHATBOT_AVATAR = ":floppy_disk:"
USER_AVATAR = ":monkey:"

# Instruction messages
WELCOME_MESSAGE = "Welcome to the chatbot! How can I assist you today?"
ERROR_MESSAGE = "I'm sorry, but I encountered an error. Please try again."

# Maximum retry attempts
LLM_API_MAX_RETRIES = 3

# Feature flags
ENABLE_FEATURE_X = True
ENABLE_FEATURE_Y = False

# Complex configurations can be nested dictionaries
ADVANCED_SETTINGS = {
    "timeout": 30,
    "cache": {
        "enabled": True,
        "max_size": 100,
        "ttl": 3600
    }
}

EXAMPLE_PROMPTS = """
How is my fabric doing?
Can you get me a list of BDs with UR enabled?
Can you add a new BD named VLAN5_BD to Tenant customerA?
How many BDs are there?
"""

TEMPERATURE = 0
