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
import xmljson
import internetarchive as ia
from configs import API_BASEURL, ES_URL

BOOK_DATA_URL = 'http://%s/BookReader/BookReaderJSON.php'
REVERSE_IMAGE_SEARCH_URL = "http://rootabout.com/search.php"
ADVANCED_SEARCH = '%s/advancedsearch.php?' % API_BASEURL
FULLTEXT_SEARCH_API = "http://books-search0.us.archive.org/api/v0.1/search"
BOOK_SEARCHINSIDE_URL = 'http://%s/fulltext/new_inside.php'


class MaxLimitException(Exception):
    pass


class InvalidJSONException(Exception):
    pass


def mimetype(f):
    return mimetypes.guess_type(f)[0]


def resolve_server(identifier):
    metadata = requests.get('%s/metadata/%s' % (API_BASEURL, identifier)).json()
    return {
        'dir': metadata['dir'],
        'server': metadata['server']
    }


def get_book_data(identifier):
    location = resolve_server(identifier)
    server = location['server']
    path = location['dir']
    r = requests.get(BOOK_DATA_URL % server, params={
        'server': server,
        'itemPath': path,
        'itemId': identifier
    })
    return r.json()

def get_wordsinside_data(bid, callback=''):
    local_path = "file://localhost//var/tmp/autoclean/derive/%s//%s.djvu" % (bid, bid)
    url = '%s/download/%s/%s' % (API_BASEURL, bid, '%s_djvu.xml' % bid)
    r = requests.get(url)
    content = r.content.replace(bytes(local_path, "utf-8"), bytes(url, "utf-8"))

    #try:
    from lxml.etree import fromstring, tostring
    from xmljson import badgerfish as bf
    xml = fromstring(content)
    return xmljson.badgerfish.data(xml)
    #except:
    #    return content        

def search_wayback(query):
    url = "https://web-beta.archive.org/__wb/search/anchor?q="
    #url = 'http://ia803500.us.archive.org/api/v1/hostsearch?q='
    r = requests.get(url + query)
    return r.json()


def get_searchinside_data(identifier, q, callback=''):
    location = resolve_server(identifier)
    server = location['server']
    path = location['dir']
    r = requests.get(BOOK_SEARCHINSIDE_URL % server, params={
        'path': path,
        'item_id': identifier,
        'doc': identifier,
        'q': q,
        'callback': callback
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
    url = FULLTEXT_SEARCH_API + '?text=%s' % text
    if collection:
        url += '&collection=%s' % collection
    r = requests.get(url)
    js = r.json()
    results = js['hits']['hits']

    def get_title(fields):
        return fields['title'][0] if 'title' in fields else ''


    if ids and names and hits:
        return {
            "results": [
                {'id': r['fields']['identifier'][0],
                 'name': get_title(r['fields']),
                 'score': r['_score'],
                 'hits': r['highlight']['text']
             } for r in results]
        }

    elif ids and names:
        return dict((r['fields']['identifier'][0],
                     get_title(r['fields'])) for r in results)

    elif names:
        return [get_title(r['fields']) for r in results]

    elif ids:
        return [r['fields']['identifier'][0] for r in results]

    return r.json()


def wayback_snapshot(url, timestamp=None):
    """
    http://web.archive.org/web/timemap/link/{URI-R}
    http://web.archive.org/web/{URI-R}
    """
    return requests.get("%s/wayback/available?url=%s"
                        % (API_BASEURL, url)).json()


def wayback_search(q):
    url = 'https://web-beta.archive.org/__wb/search/host?q='
    r = requests.get(url + q)
    return r.json()


def collections(collection_id=None, page=1, limit=100, security=True):
    if collection_id:
        q = "collection:(%s)" % collection_id
    else:
        q = "mediatype:collection AND NOT identifier:fav-*"
    return search(q, page=page, limit=limit, security=security)


def apiv1():
    r = requests.post('%s/advancedsearch.php?' % API_BASEURL)
    return r.json()


def get_arcade_games(query=None, page=1, limit=1000):
    q = '(collection:(apple_ii_library_games_asimov) OR ' \
        'collection:(atari_8bit_library_educational) OR ' \
        'collection:(atari_8bit_library_games) OR ' \
        'collection:(gamegear_library) OR ' \
        'collection:(gamepocket_library) OR ' \
        'collection:(softwarelibrary_apple2gs_games) OR ' \
        'collection:(softwarelibrary_msdos_games) OR ' \
        'collection:(softwarelibrary_win3_games) OR ' \
        'collection:(zx_spectrum_library_games) OR ' \
        'collection:(apple_ii_library_games)) AND ' \
        'mediatype:"software" AND ' \
        'emulator:*' + ((' AND %s' % query) if query else '')
    return search(q, page=page, limit=limit, sort="sort%5B%5D=downloads+desc")

def search(query, page=1, limit=100, security=True, sort=None, fields=None):
    if not query:
        raise ValueError("GET query parameters 'q' required")

    if int(limit) > 1000 and security:
        raise MaxLimitException("Limit may not exceed 1000.")

    sort = sort or 'sort%5B%5D=date+asc&sort%5B%5D=createdate'
    fields = fields or 'identifier,title'
    return requests.get(
        ADVANCED_SEARCH + sort,
        params={'q': query,
                'rows': limit,
                'page': page,
                'fl[]': fields,
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
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.findAll('table', {'class': 'metatable'})[0]
        return [x.nextSibling.text for x in
                table.findAll('td', text="Identifier:")]
    except:
        return []
