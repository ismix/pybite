from base.proxybase import ProxyBase
import stem.process as sp
from stem.control import Controller as Sc
from stem import Signal
import config


class TorClient(ProxyBase):
    """
    Python client for Tor proxy.
    """

    proxy_addr = 'localhost'

    def __init__(self):
        super(self.__class__, self).__init__()

        self.socks_port = config.TOR_SOCKS_PORT
        self.control_port = config.TOR_CONTROL_PORT
        self.proxy_port = self.socks_port
        self.tor_process = sp.launch_tor_with_config(
            config={
                'SocksPort': str(self.socks_port),
                'ExitNodes': config.TOR_EXIT_NODES,
                'ExcludeNodes': config.TOR_EXCLUDE_NODES,
                'ExcludeExitNodes': config.TOR_EXCLUDE_NODES,
                'StrictNodes': '1',
                'MaxCircuitDirtiness': config.TOR_MAX_CIRCUIT_DIRTINESS
            }
        )

    def change_identity(self):
        with Sc.from_port(port=self.control_port) as tor_controller:
            tor_controller.authenticate(password=config.TOR_PASSWORD)
            tor_controller.signal(Signal.NEWNYM)

    def stop(self):
        self.tor_process.kill()

if __name__ == "__main__":
    t = TorClient()

    for i in range(2):
        print t.get_page('https://www.atagar.com/echo.php')
        t.change_identity()

    t.stop()