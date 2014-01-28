"""
This module consists of helper utilities that can be used for locational purposes.
"""

import json
import os


def get_us_zipcodes_by_state():
    """
    Returns all US zipcodes with state and city information.

    @rtype: list
    @returns: A list of 3d tuples, first item is a list of zip codes, second and third items are city and state
    (respectively) those zipcodes belong to.
    """
    resource_path = os.path.join(os.path.dirname(__file__), '../data/zipcodes.json')
    with open(resource_path) as zipcode_file:
        zipcode_data = json.load(zipcode_file)

    return zipcode_data
