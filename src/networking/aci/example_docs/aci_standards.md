# Cisco ACI Configuration Guidelines for LLM

This guideline is to help facilitate autonomous agents of LLM  
This document describes the policy and standards to be followed when configuring the Cisco ACI fabric.  
All LLM configurations must strictly follow this guideline. This is a living document and will be updated frequently.

## Glossary and Abbreviations
* TN = Tenant
* AP = Application Profile
* EPG = Endpoint Group
* BD = Bridge Domain

## Naming Conventions
* All new objects that the user wants to create shall be in all caps, no CamelCase or lowercase allowed. e.g. VRF_PROD
* All new objects that the user wants to create shall be concatenated with underscore `_` only, `-`, or `.` shall not be used
* When numbers are involved, digit paddings must be used, Bridge Domains uses 4 digits padding, whereas interface numbers uses 2 digit padding.
* When registering new Leafs, must follow the following format `LEAF<number>`

## Creating new Bridge Domains
* BDs always follow the naming convention of `BD_VLAN<vlan_id>`, where `vlan_id` should be a 4 digit, with 0s as paddings if less than 4 digit
* Unicast routing must be enabled for all BDs, there are no layer2 BDs in the environment
* All BDs must be associated with the L3Out `OSPF_L3OUT` for advertising the routes out
* All BDs must have `ARP flooding enabled` and `L2unknown unicast set to flood` to compensate for silent hosts
* All BDs must have GARP detection enabled
* All subnets must have `public` and `primary` flags checked

## Creating new EPGs
* Before creating new EPGs, ensure that the Tenant, AP already exists
* EPGs should always follow the naming convention of `EPG_VLAN<vlan_id>` with paddings of 0s as well
* A domain must be associated first, we use `VMM_DOM` for VMWare, and `VMM_PHYS` for static paths
* All EPGs must have `preferred group` set as `included`