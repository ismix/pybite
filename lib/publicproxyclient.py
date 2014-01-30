from base.proxybase import ProxyBase
from toolbox.proxy import get_public_proxy_list
import pycurl
import config


class PublicProxyClient(ProxyBase):
    proxy_type = pycurl.PROXYTYPE_HTTP

    def __init__(self):
        super(self.__class__, self).__init__(config.PUBLIC_PROXY_TIMEOUT)

        self.proxies = get_public_proxy_list()
        self.proxy_index = 0
        self.num_proxies = len(self.proxies)

        first_proxy = self.proxies[self.proxy_index]
        self._set_proxy(first_proxy)

    def _set_proxy(self, proxy):
        self.proxy_addr = proxy[0]
        self.proxy_port = proxy[1]

    def change_identity(self):
        self.proxy_index = (self.proxy_index+1) % self.num_proxies

        new_proxy = self.proxies[self.proxy_index]
        self._set_proxy(new_proxy)
