"""

All open AI functions definitions are defined here

"""
from src.llm_api.utils.helper import create_function_config

show_cmd_function = create_function_config(
    name="show_cmd",
    description="execute various nxos show commands",
    properties={
        "cmd": {
            "type": "string",
            "description": "show command(s) to be executed, multiple commands can be separated with ';' "
        }
    },
    required=["cmd"]
)


get_configuration_guideline_function = create_function_config(
    name="get_configuration_guideline",
    description="Get guidelines for ACI policy standards,",
    properties={
        "query": {
            "type": "string",
            "description": "query from the network admin"
        }
    },
    required=["query"]
)


get_bd_function = create_function_config(
    name="get_bd",
    description="Get information about bridge domains (BD)",
    properties={
        "unicastRoute": {
            "type": "string",
            "description": "unicast routing(UR) settings",
            "enum": ["yes", "no"]
        },
        "unkMacUcastAct": {
            "type": "string",
            "description": "L2 Unknown unicast setting",
            "enum": ["flood", "proxy"]
        },
        "operator": {
            "type": "string",
            "description": "operators are used to filter and concatenate different properties",
            "enum": ["wcard", "and", "or", "bw", "lt", "gt"]
        }
    },
    required=[]
)

# This defines the function and how the function works
get_fabric_health_function = create_function_config(
    name="get_fabric_health",
    description="Get the latest fabric health, provide user min, max and average for the past 5 minutes",
    properties={},
    required=[]
)

get_tenant_function = create_function_config(
    name="get_tenant",
    description="Get Tenant information for end user",
    properties={},
    required=[]
)

get_vrf_function = create_function_config(
    name="get_vrf",
    description="Get VRF information for end user",
    properties={
        "tenantName": {
            "type": "string",
            "description": "name of the Tenant where the VRF is configured under"
        },

        "vrfName": {
            "type": "string",
            "description": "name of the VRF to get information from"
        },
    },
    required=[]
)


build_bd_function = create_function_config(
    name="create_bd",
    description="Create a bridge domain using inputs from user",
    properties={
        "tenantName": {
            "type": "string",
            "description": "name of the Tenant to deploy to"
        },
        "bdName": {
            "type": "string",
            "description": "name of the bridge domain"
        },
        "vrfName": {
            "type": "string",
            "description": "name of the VRF, required from user",
        },
        "unicastRoute": {
            "type": "string",
            "description": "unicast routing",
            "enum": ["yes", "no"]
        },
        "garp": {
            "type": "string",
            "description": "GARP mode",
            "enum": ["garp", ""]
        },
        "L2UnknownUnicast": {
            "type": "string",
            "description": "L2 unknown unicast setting",
            "enum": ["flood", "proxy"]
        },
        "arpFlood": {
            "type": "string",
            "description": "ARP Flood settings",
            "enum": ["yes", "no"]
        },
        "l3outs": {
            "type": "string",
            "description": "a list of l3out to be added to the bridge domain",
        },
        "subnets": {
            "type": "string",
            "description": "a list of subnet to be associated with the bridge domain, "
                           "subnet must follow this specific format '<subnet IP>|<preferred>|<scope>', "
                           "'preferred' can only be 'yes' or 'no', "
                           "'scope' can only be 'public', 'public+shared', or 'private+shared'"
                           "for example: 1.1.1.1/24|yes|public+shared",
        }
    },
    required=["tenantName", "bdName", "vrfName"]
)