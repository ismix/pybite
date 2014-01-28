import os
import json


def get_public_proxy_list():
    """
    Returns all US proxies with ip and port.

    @rtype: list
    @returns: List of lists, first item in inner list is ip and the second is port.
    """
    resource_path = os.path.join(os.path.dirname(__file__), '../data/publicproxies.lst')
    proxies = []
    with open(resource_path) as proxies_file:
        for line in proxies_file.readlines():
            proxy = line.strip().split(':')
            proxies.append((proxy[0], int(proxy[1])))

    return proxies

