import json
from urllib.error import URLError
import sys


class MoQuery(object):
    def __init__(self, session, full_url=None, dn=None, cls=None, rsp_subtree=None, target_subtree_cls=None, rsp_subtree_cls=None,
                 rsp_subtree_inc=None, target_flt=None, target=None, rsp_subtree_flt=None, rsp_prop_include=None,
                 page_size=None, order_by=None):
        self.__options = {}
        if dn:
            self.dn = dn
            self.base_url = f'/api/mo/{dn}.json'
        elif cls:
            self.cls = cls
            self.base_url = f'/api/class/{cls}.json'
        elif full_url:
            self.base_url = f'/api/{full_url}'
        else:
            sys.exit('you must enter at least either a DN, or a class')
        self.session = session
        # create a dictionary with options user entered
        if rsp_subtree:
            self.__options.update({'rsp-subtree': rsp_subtree})
        if rsp_subtree_cls:
            self.__options.update({'rsp-subtree-class': rsp_subtree_cls})
        if target:
            self.__options.update({'query-target': target})
        if target_subtree_cls:
            self.__options.update({'target-subtree-class': target_subtree_cls})
        if target_flt:
            self.__options.update({'query-target-filter': target_flt})
        if rsp_subtree_flt:
            self.__options.update({'rsp-subtree-filter': rsp_subtree_flt})
        if rsp_prop_include:
            # {all | naming-only | config-only}
            self.__options.update({'rsp-prop-include': rsp_prop_include})
        if page_size:
            self.__options.update({'page-size': str(page_size)})
        if order_by:
            self.__options.update({'order-by': self.cls + '.' + order_by})
        if rsp_subtree_inc:
            self.__options.update({'rsp-subtree-include': rsp_subtree_inc})

    def has_mo(self):
        # return true if there is mo
        return self.response_data_json()['totalCount'] != '0'

    def __option_url(self):
        """
        Concatenate different options, same as concatenating -x options in moquery
        """
        opt_string = ''
        if self.__options:
            opt_string = '?' + '&'.join(f'{key}={value}' for key, value in self.__options.items())
        return opt_string

    def _request_url(self):
        return self.base_url + self.__option_url()

    def response(self):
        return self.session.get(self._request_url())

    def response_data_json(self) -> json:
        if self.response().status_code == 200:
            return self.response().json()
        else:
            raise URLError(json.loads(self.response().text)['imdata'])

    def children(self):
        for k, v in self.__options.items():
            if v == 'children' or v == 'full':
                try:
                    return self.response_data_json()['imdata'][0][self.cls]['children']
                except IndexError:
                    print(f"No child found with URI {self._request_url()}")
                    return None

    def self_attr(self):
        return self.response_data_json()['imdata'][0][self.cls]['attributes']

    def imdata(self):
        if not self.has_mo():
            return {}
        return self.response_data_json()['imdata']