import siteparser
from lib.torclient import TorClient
from lib.publicproxyclient import PublicProxyClient
from lib.dbclient import DbClient


class Collector:
    def __init__(self, parser_name, keyword, use_proxy=None, parser_params=None):
        if use_proxy == 'tor':
            self.proxy_client = TorClient()
        elif use_proxy == 'public':
            self.proxy_client = PublicProxyClient()
        else:
            self.proxy_client = None

        parser_name = parser_name.title()+'Parser'

        self.parser = getattr(siteparser, parser_name)(keyword, parser_params, proxy_client=self.proxy_client)
        key_fields = self.parser.get_key_fields()
        self.db = DbClient(key_fields)

    def start(self):
        for data in self.parser.process_batch():
            self._save_data(data)
            self._do_interbatch()

        if self.proxy_client is not None:
            self.proxy_client.stop()

    def _do_interbatch(self):
        if self.proxy_client is None:
            pass  # TODO: Maybe wait for some time etc.
        else:
            pass  # TODO: self.proxy_client.change_identity() doesnt work as expected

    def _save_data(self, data):
        self.db.add_bulk_data(data)