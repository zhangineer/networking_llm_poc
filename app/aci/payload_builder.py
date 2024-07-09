"""
This module handles tasks to construct payload
"""
from jinja2 import Environment, FileSystemLoader
from typing import Dict
import json


class PayloadBuilder:
    def __init__(self):
        pass

    @staticmethod
    def render_jinja(template_name, data, folder):
        e = Environment(
            lstrip_blocks=True,
            loader=FileSystemLoader(folder)
        )
        return e.get_template(template_name).render(data)

    def build_payload(self, template_name: str, data: Dict) -> Dict:
        """
        Build JSON payload using Jinja Templates
        Args:
            template_name: name of the template to use, without the .extension
            data: The payload data in dictionary format

        Returns:
            returns a constructed JSON data based on jinj2 template
        """
        payload = json.loads(self.render_jinja(f"{template_name}.j2", data,
                                               "app/aci/aci_j2_templates"))
        return payload

    def build_tenant_payload(self, tn_name: str) -> Dict:
        """
        Build the data payload for a bridge domain object
        Args:
            tn_name: Tenant name

        Returns:
            Data payload in JSON format for sending to the APIC
        """

        return self.build_payload(template_name='tenant', data={'tn_name': tn_name})

    def build_bd_payload(self, tn_name: str, bd_name: str, vrf_name: str, **kwargs) -> Dict:
        """
        Build the data payload for a bridge domain object
        Args:
            tn_name: Tenant name
            bd_name: Bridge Domain name
            vrf_name: VRF name
            **kwargs: additional parameters

        Returns:
            Data payload in JSON format for sending to the APIC
        """

        bd_self_data = {
            'tn_name': tn_name,
            'bd_name': bd_name,
            'vrf_name': vrf_name,
            'l3out_payload': [],
            'subnet_payload': [],
            'ucr': str(kwargs.get("unicastRoute", '')).lower(),
            'unk_uc': str(kwargs.get('L2UnknownUnicast', '')).lower(),
            'arp': str(kwargs.get('arpFlood', '')).lower(),
            'garp': str(kwargs.get('garp', '')).lower(),
            'l3outs': str(kwargs.get('l3outs', '')),
            'subnets': str(kwargs.get('subnets', ''))
        }
        if bd_self_data['l3outs']:
            l3outs = bd_self_data['l3outs'].strip().replace(' ', '').split(',')
            for l3out in l3outs:
                l3out_rs_data = {'l3out': l3out}
                bd_self_data['l3out_payload'].append(
                    self.build_payload('l3out_rs', l3out_rs_data)
                )
        if bd_self_data['subnets']:
            subnets = bd_self_data['subnets'].strip().replace(' ', '').split(',')
            for subnet in subnets:
                subnet_attributes = subnet.split('|')
                subnet_data = {'subnet': subnet_attributes[0], 'preferred': subnet_attributes[1], 'scope': subnet_attributes[2].replace("+",",")}
                bd_self_data['subnet_payload'].append(
                    self.build_payload('subnet', subnet_data)
                )
        payload = self.build_payload(template_name='bd', data=bd_self_data)
        return payload
