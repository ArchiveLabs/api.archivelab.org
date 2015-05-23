#!/usr/bin/env python
#-*-coding: utf-8 -*-

"""
    api.py
    ~~~~~~
    A collection of methods for retrieving data from Internet Archive services.

    :copyright: (c) 2015 by Internet Archive
    :license: see LICENSE for more details.
"""

import json
import requests
import mimetypes
from configs import API_BASEURL

class MaxLimitException(Exception):
    pass

class InvalidJSONException(Exception):
    pass

def mimetype(f):
    return mimetypes.guess_type(f)[0]

def item(iid):
    try:
        return requests.get('%s/details/%s' % (API_BASEURL, iid),
                            params={"output": "json"}).json()
    except ValueError as v:
        return v

def download(iid, filename):
    r = requests.get('%s/download/%s/%s' % (API_BASEURL, iid, filename),
                     stream=True, allow_redirects=True)
    f = ""
    if not r.ok:
        return None # raise exception

    for chunk in r.iter_content(chunk_size=1024):
        if chunk:
            f += chunk
    return f

def snapshot(url, timestamp=None):
    """
    http://web.archive.org/web/timemap/link/{URI-R}
    http://web.archive.org/web/{URI-R}
    """
    return requests.get("%s/wayback/available?url=%s"
                        % (API_BASEURL, url)).json()

def collections(collection_id=None, page=1, limit=100):
    if collection_id:
        q = "collection:(wb_urls)"
    else:
        q = "mediatype:collection AND NOT identifier:fav-*"
    r = search(q, page=page, limit=limit)['response']
    r['limit'] = limit
    r['next'] = r['start'] + limit + 1
    return r

def search(query, page=1, limit=100):
    if int(limit) > 1000:
        raise MaxLimitException("Limit may not exceed 1000.")
    return requests.get('%s/advancedsearch.php' % API_BASEURL,
                        params={'q': query,
                                'rows': limit,
                                'page': page,
                                'fl[]': 'identifier',
                                'output': 'json'
                                }).json()

    

