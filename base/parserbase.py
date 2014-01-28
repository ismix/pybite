from abc import ABCMeta, abstractmethod
import urllib2
from base.proxybase import UnreachableError
import config


class ParserBase(object):
    """
    Base class for parser classes. All parser classes should extend this class and implement the abstract methods.
    """
    __metaclass__ = ABCMeta

    def __init__(self, proxy_client=None):
        """
        If tor client exists, then change get page method to use cURL with proxy. All parsers should use _get_page
        method when requesting the page content.

        Also subclassing parser should except tor_client parameter and pass it to ParserBase __init__ method.
        """
        if proxy_client is None:
            self._get_page = self._get_page_basic
        else:
            self.proxy_client = proxy_client
            self._get_page = self._get_page_with_proxy

    @abstractmethod
    def process_batch(self):
        """
        A generator function which yields current batch and waits for interbatch operations. Batch size is defined with
        each parser, it can be a page of listing, all pages of a specific search, or a limited number.

        @rtype: list
        @return: List of all parsed results.
        """
        pass

    @abstractmethod
    def get_key_fields(self):
        """
        Key fields that subclassing parser uses in the record that it uses. For key types, refer to
        lib.dbclient module.

        @rtype: dict
        @return Dictionary of list of keys that record uses.
        """
        pass

    def _get_page_with_proxy(self, url):
        """
        Get page method with tor or public proxy, using cURL with proxy.
        """
        for i in range(config.MAXIMUM_RETRY):
            try:
                content = self.proxy_client.get_page(url)
                return content
            except UnreachableError as ex:
                self.proxy_client.change_identity()

        raise UnreachableError(ex.message)

    def _get_page_basic(self, url):
        """
        Simple get page method with urllib2.
        """
        content = urllib2.urlopen(url).read()
        return content


class BlockedError(Exception):
    pass
