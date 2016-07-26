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
import base64
import mimetypes
import internetarchive as ia
from bs4 import BeautifulSoup
from configs import API_BASEURL, ES_URL

BOOK_DATA_URL = 'http://%s/BookReader/BookReaderJSON.php'
REVERSE_IMAGE_SEARCH_URL = "http://rootabout.com/search.php"
ADVANCED_SEARCH = '%s/advancedsearch.php?' % API_BASEURL
FULLTEXT_SEARCH_API = "https://books-search0.us.archive.org/api/dev/v0.1/search"


class MaxLimitException(Exception):
    pass


class InvalidJSONException(Exception):
    pass


def mimetype(f):
    return mimetypes.guess_type(f)[0]


def get_book_data(identifier):
    metadata = requests.get('%s/metadata/%s' % (API_BASEURL, identifier)).json()
    server = metadata['server']

    r = requests.get(BOOK_DATA_URL % server, params={
            'server': server,
            'itemPath': metadata['dir'],
            'itemId': identifier
    })
    return r.json()


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
    if '.____padding_file/' in filename and 'Host' in h:
        del h['Host']
    url = '%s/download/%s/%s' % (API_BASEURL, iid, filename)

    r = requests.get(url, stream=True, allow_redirects=True,
                     verify=False, headers=h)
    if not r.ok:
        # print('curl -v -L -i -H ',
        # ' -H '.join("'%s: %s'" % i for i in r.request.headers.items()), r.request.url)
        return None  # raise exception
    return r


def fulltext_search(text, collection=None, ids=False, names=False, hits=False):
    url = FULLTEXT_SEARCH_API + '?text="%s"' % text
    if collection:
        url += '&collection=%s' % collection
    r = requests.get(url)
    js = r.json()
    results = js['hits']['hits']

    if ids and names and hits:
        return dict((r['fields']['identifier'][0], {
            'name': r['fields']['title'][0],
            'hits': r['highlight']['text']
        }) for r in results)

    elif ids and names:
        return dict((r['fields']['identifier'][0],
                     r['fields']['title'][0]) for r in results)

    elif names:
        return [r['fields']['title'][0] for r in results]

    elif ids:
        return [r['fields']['identifier'][0] for r in results]

    return r.json()


def snapshot(url, timestamp=None):
    """
    http://web.archive.org/web/timemap/link/{URI-R}
    http://web.archive.org/web/{URI-R}
    """
    return requests.get("%s/wayback/available?url=%s"
                        % (API_BASEURL, url)).json()


def collections(collection_id=None, page=1, limit=100, security=True):
    if collection_id:
        q = "collection:(%s)" % collection_id
    else:
        q = "mediatype:collection AND NOT identifier:fav-*"
    return search(q, page=page, limit=limit, security=security)


def apiv1():
    r = requests.post('%s/advancedsearch.php?' % API_BASEURL)
    return r.json()


def search(query, page=1, limit=100, security=True):
    if int(limit) > 1000 and security:
        raise MaxLimitException("Limit may not exceed 1000.")
    return requests.get(
        ADVANCED_SEARCH + 'sort%5B%5D=date+asc&sort%5B%5D=createdate',
                        params={'q': query,
                                'rows': limit,
                                'page': page,
                                'fl[]': 'identifier,title',
                                'output': 'json',
                                }).json()


def reverse_image_search(filename, base64img):
    mime = "data:%s;base64," % mimetype(filename)
    r = requests.post(REVERSE_IMAGE_SEARCH_URL, data={
        "searchimg": "%s,%s" % (mime, base64img),
        "limit": "5",
        "search": "ia"
    })
    html = r.content
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.findAll('table', {'class': 'metatable'})[0]
    return [x.nextSibling.text for x in
            table.findAll('td', text="Identifier:")]
