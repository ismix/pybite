import pycurl
import StringIO
from abc import ABCMeta, abstractmethod


class ProxyBase(object):
    __metaclass__ = ABCMeta

    proxy_addr = 'localhost'
    proxy_port = None
    proxy_type = pycurl.PROXYTYPE_SOCKS5

    def __init__(self, timeout=None):
        self.timeout = timeout

    @abstractmethod
    def change_identity(self):
        pass

    def stop(self):
        pass

    def get_page(self, url):
        output = StringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.PROXY, self.proxy_addr)
        c.setopt(pycurl.PROXYPORT, self.proxy_port)
        c.setopt(pycurl.PROXYTYPE, self.proxy_type)
        c.setopt(pycurl.WRITEFUNCTION, output.write)
        c.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:8.0) Gecko/20100101 Firefox/8.0')

        if not (self.timeout is None):
            c.setopt(pycurl.TIMEOUT, self.timeout)

        try:
            c.perform()
            c.close()
            return output.getvalue()
        except pycurl.error as exc:
            raise UnreachableError('We couldn\'t get the page: '+url)


class UnreachableError(Exception):
    pass
