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
from configs import API_BASEURL, ES_URL


class MaxLimitException(Exception):
    pass


class InvalidJSONException(Exception):
    pass


def mimetype(f):
    return mimetypes.guess_type(f)[0]


def items(iid=None, page=1, limit=100, filters=""):
    # aaron's idea: Weekly dump of ID of all identifiers (gzip)
    # elastic search query w/ paging
    if iid:
        return item(iid)
    # 'all:1' also works
    q = "NOT identifier:..*" + (" AND (%s)" % filters if filters else "")
    return search(q, page=page, limit=limit)


def item(iid):
    try:
        return requests.get('%s/metadata/%s' % (API_BASEURL, iid)).json()
    except ValueError as v:
        return v


def download(iid, filename, headers=None):
    h = dict(headers) if headers else {}
    h['Accept-Encoding'] = ''
    if 'Content-Length' in h:
        del h['Content-Length']
    url = '%s/download/%s/%s' % (API_BASEURL, iid, filename)
    r = requests.get(url, stream=True, allow_redirects=True,
                     verify=False, headers=h)
    if not r.ok:
        return None  # raise exception
    return r


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
    return search(q, page=page, limit=limit)


def apiv1():
    r = requests.post('%s/advancedsearch.php?' % API_BASEURL)
    return r.json()


def search(query, page=1, limit=100):
    if int(limit) > 1000:
        raise MaxLimitException("Limit may not exceed 1000.")

    return requests.get('%s/advancedsearch.php?' % API_BASEURL + 'sort%5B%5D=date+asc&sort%5B%5D=createdate',
                        params={'q': query,
                                'rows': limit,
                                'page': page,
                                'fl[]': 'identifier,title',
                                'output': 'json',
                                }).json()
