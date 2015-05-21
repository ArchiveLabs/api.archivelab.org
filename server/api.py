#!/usr/bin/env python
#-*-coding: utf-8 -*-

"""
    api.py
    ~~~~~~
    A collection of methods for retrieving data from Internet Archive services.

    :copyright: (c) 2015 by Internet Archive
    :license: see LICENSE for more details.
"""

import requests

BASEURL = "https://archive.org"

class MaxLimitException(Exception):
    pass

class InvalidJSONException(Exception):
    pass

def item(iid):
    try:
        return requests.get('%s/details/%s' % (BASEURL, iid),
                            params={"output": "json"}).json()
    except ValueError:
        return None   

def search(query, page=1, limit=100):
    if limit > 1000:
        raise MaxLimitException("Limit may not exceed 1000.")
    return requests.get('%s/advancedsearch.php' % BASEURL,
                        params={'q': query,
                                'rows': limit,
                                'page': page,
                                'fl[]': 'identifier',
                                'output': 'json'
                                }).json()

    

