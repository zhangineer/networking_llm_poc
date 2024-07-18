import os

from src.networking.aci.acisession import Session
from dotenv import load_dotenv, find_dotenv
from src.networking.aci.moquery import MoQuery
from src.networking.aci.payload_builder import PayloadBuilder
from src.llm_api.utils.helper import register

_ = load_dotenv((find_dotenv()))


class BaseACIClient:
    """
    This class is for interacting with the Cisco ACI API
    """

    def __init__(self,
                 apic=os.getenv('APIC_IP'),
                 apic_username=os.getenv('APIC_USERNAME'),
                 apic_password=os.getenv('APIC_PASSWORD')):
        self.apic = apic
        self.apic_username = apic_username
        self.apic_password = apic_password
        self.apic_port = os.getenv('APIC_PORT', 443)
        self.rest_session = None

    def initiate_rest(self):
        self.rest_session = Session(f"https://{self.apic}:{self.apic_port}", uid=f"{self.apic_username}",
                                    pwd=f"{self.apic_password}")
        self.rest_session.login()

    def get_version(self):
        query = MoQuery(self.rest_session, dn="mo/sys/showversion.json")
        return query.imdata()


class TenantOperation(BaseACIClient):
    @register
    def get_tenant(self):
        """
        Get a list of all tenants
        """
        query = MoQuery(self.rest_session, cls="fvTenant")
        return query.imdata()

    def create_tenant(self, name):
        """
        Create a new Tenant
        """
        payload_builder = PayloadBuilder()
        data = payload_builder.build_tenant_payload(name)
        resp = self.rest_session.push_to_apic(data)
        return resp.status_code, resp.json()

    @register
    def get_bd(self, **target_filters):
        """
        Get Bridge Domain related information
        """
        flt_parts = [f"eq(fvBD.{key},\"{value}\")" for key, value in target_filters.items()]
        if flt_parts:
            target_filters = "and(" + ",".join(flt_parts) + ")"
            query = MoQuery(self.rest_session, cls="fvBD", target_flt=target_filters)
            return query.imdata()
        query = MoQuery(self.rest_session, cls="fvBD")
        return query.imdata()

    @register
    def create_bd(self, **attributes):
        payload_builder = PayloadBuilder()
        data = payload_builder.build_bd_payload(
            attributes.get('tenantName'),
            attributes.get('bdName'),
            attributes.get('vrfName'),
            **attributes
        )
        resp = self.rest_session.push_to_apic(data)
        return resp.status_code, resp.json()

    @register
    def get_vrf(self, **target_filters):
        flt_parts = [f"eq(fvCtx.{key},\"{value}\")" for key, value in target_filters.items()]
        if flt_parts:
            target_filters = "and(" + ",".join(flt_parts) + ")"
            query = MoQuery(self.rest_session, cls="fvCtx", target_flt=target_filters)
            return query.imdata()
        query = MoQuery(self.rest_session, cls="fvCtx")
        return query.imdata()


class FabricOperation(BaseACIClient):
    @register
    def get_fabric_health(self):
        """
        Retrieve the overall fabric healthscore
        """
        query = MoQuery(self.rest_session, dn='topology/HDfabricOverallHealth5min-0')
        return query.imdata()

    @register
    def get_fault_count(self):
        query = MoQuery(self.rest_session, cls='faultInst', target_flt='ne(faultInst.severity,"cleared")')
        return query.imdata()