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
import time
import requests
import base64
import mimetypes
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO, BytesIO

import xmljson
import internetarchive as ia
from configs import API_BASEURL, ES_URL, iiif_url

SCRAPE_API = '%s/services/search/v1/scrape' % API_BASEURL
BOOK_DATA_URL = 'http://%s/BookReader/BookReaderJSON.php'
BOOK_PAGE_URL = 'http://%s/BookReader/BookReaderImages.php'
REVERSE_IMAGE_SEARCH_URL = "http://rootabout.com/search.php"
ADVANCED_SEARCH = '%s/advancedsearch.php?' % API_BASEURL
FULLTEXT_SEARCH_API = "http://books-search0.us.archive.org/api/v0.1/search"
BOOK_SEARCHINSIDE_URL = 'http://%s/fulltext/inside.php'
LOAN_URL = 'https://archive.org/services/loans/beta/loan/index.php?action=%s&identifier=%s&access=%s&secret=%s'
BOOK_OCR_URL = 'https://%s/BookReader/BookReaderGetTextWrapper.php'

OL_API = 'https://openlibrary.org/ia/%s.json'

class MaxLimitException(Exception):
    pass


class InvalidJSONException(Exception):
    pass


def mimetype(f):
    return mimetypes.guess_type(f)[0]

def resolve_server(identifier):
    """
    Returns:
      a dict containing this item's:
        server: e.g. ia601507.us.archive.org
        dir: on disk containing files, e.g. /2/items/recurringwordsth00ethe
    """
    metadata = requests.get('%s/metadata/%s' % (API_BASEURL, identifier)).json()
    return {
        'metadata': metadata,
        'dir': metadata['dir'],
        'server': metadata['server']
    }

def tts_url(identifier, text):
    server = (resolve_server(identifier) or {}).get('server', 'ia601507.us.archive.org')
    url = 'https://%s/BookReader/BookReaderGetTTS.php?string=%s&format=.mp3' \
          % (server, text)
    return url

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


def get_book_page(identifier, page, url_root):
    """Retrieves a specific page from a book, assuing the book has no
    special privileges
    """
    url = '%s/%s$%s/full/full/0/default.jpg' % (iiif_url, identifier, page)
    r = requests.get(url, params={'domain': '%siiif/' % url_root}, stream=True,
                     allow_redirects=True, timeout=None)
    return r


def get_toc_page(identifier, page):
    """This should only be called by methods who can guarantee page is a
    Table of Contents page. Bypasses lending restrictions
    """
    location = resolve_server(identifier)
    server = location['server']
    path = location['dir']

    url = BOOK_PAGE_URL % (server)
    url += '?id=%s&itemPath=%s&server=%s&page=leaf%s' % (identifier, path, server, page)
    r = requests.get(url, stream=True)
    strIO = StringIO()
    strIO.write(r.content)
    strIO.seek(0)
    return strIO

def time2sec(t):
    """Converts h:m:s to int(sec)
    https://stackoverflow.com/questions/10663720/converting-a-time-string-to-seconds-in-python
    """
    t = str(t)
    if t.count(':') == 1:
        pt = time.strptime(t,'%M:%S')
        total_seconds = pt.tm_sec + (pt.tm_min * 60)
    elif t.count(':') == 2:
        pt = time.strptime(t,'%H:%M:%S')
        total_seconds = pt.tm_sec + (pt.tm_mind * 60) + (pt.tm_hour * 3600)
    return total_seconds

def get_book_opds_audio_manifest(identifier, url_root):
    data = item(identifier)
    metadata = data['metadata']
    reading_order = []
    _tracks = data.get(identifier) or data.get('files')
    sorter = lambda x: int(x.get('track', '') \
                           if '/' not in x.get('track') \
                           else x.get('track').split('/')[0])
    tracks = sorted([track for track in _tracks if
                     track.get('bitrate') and track.get('track')],
                    key=sorter)
    for t in tracks:
        reading_order.append(
            {"href": "%s/download/%s/%s" % (
                API_BASEURL, identifier, t.get('name')),
             "type": "audio/mpeg", "bitrate": t.get('bitrate'),
             "duration": time2sec(t['length']), "title": t.get('title')
            })
    manifest_url = url_root + 'books/%s/opds_audio_manifest' % identifier
    links = [
        {"href": "%s/services/img/%s" % (API_BASEURL, identifier),
         "rel": "cover", "type": "image/jpeg",
         "height": 180, "width": 180},
        {"href": manifest_url,
         "rel": "self", "type": "application/audiobook+json"}
    ]
    librivox_id = metadata.get('external-identifer') and metadata.get('external-identifer').split('urn:librivox_id:')[1]
    # Call Librivox API to get narrator info ...
    return {
        "@context": "http://readium.org/webpub-manifest/context.jsonld",
        "metadata": {
            "tracks": len(reading_order),
            "@type": "https://schema.org/Audiobook",
            # "@id": librivox_id,  # schema:identifier
            "identifier": '%s/details/%s' % (API_BASEURL, identifier),
            "title": metadata.get('title'),
            "author": metadata.get('creator'),
            #"narrator": [],
            "language": metadata.get('language', 'en'),
            #"publisher": metadata.get('publisher'),
            #"published": "2016-02-01",
            #"modified": "2016-02-18T10:32:18Z",
            "duration": sum(t['duration'] for t in reading_order)
        },
        "links": links,
        "readingOrder": reading_order
    }


def get_book_iiif_manifest(identifier, url_root):
    url = "%s/%s/manifest.json" % (iiif_url, identifier)
    r = requests.get(url, params={'domain': '%siiif/' % url_root},
                    allow_redirects=True)
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

def get_book_fulltext(identifier, stringio=False):
    metadata = requests.get('%s/metadata/%s' % (API_BASEURL, identifier)).json()
    location = {
        'dir': metadata['dir'],
        'server': metadata['server']
    }
    location = resolve_server(identifier)
    server = location['server']
    for f in metadata['files']:
        if f['name'].endswith('_djvu.txt'):
            url = 'https://archive.org/download/%s/%s' % (identifier, f['name'])
            r = requests.get(url)
            if stringio:
                bio = BytesIO()
                bio.write(r.content)
                bio.seek(0)
                return bio
            return r.content

def get_bookpage_annotations(identifier, page):
    url = 'https://pragma.archivelab.org/annotations?canvas_id='
    url = url + "%s/%s$%s/canvas" % (iiif_url, identifier, page)
    r = requests.get(url)
    return r.json()

def get_book_annotations(identifier, crosslinks=None):
    url = 'https://pragma.archivelab.org/annotations?ocaid=%s' % identifier
    if crosslinks:
        url += '&crosslinks=true'
    r = requests.get(url)
    return r.json()

def get_scandata_xml(identifier):
    from lxml.etree import fromstring, tostring
    from xmljson import badgerfish as bf
    location = resolve_server(identifier)
    server = location['server']
    path = location['dir']
    r = requests.get('%s/download/%s/%s_scandata.xml' % (
        API_BASEURL, identifier, identifier))
    xml = fromstring(r.content)
    return xmljson.badgerfish.data(xml)

def get_toc(identifier):
    scandata = get_scandata_xml(identifier)
    pages = scandata['book']['pageData']['page']
    toc_pages = [pages[i]['@leafNum'] for i, page in enumerate(pages) if
                 pages[i]['pageType']['$'] == 'Contents']
    return toc_pages

def get_bookpage_ocr(identifier, page, mode="paragraphs", access=None, secret=None):
    cookies = {}
    if access and secret:
        try:
            r = requests.post(LOAN_URL % ('create_token', identifier, access, secret))
            if r.json()['success']:
                cookies['loan-%s' % identifier] = r.json()['token']
        except:
            pass
    metadata = requests.get('%s/metadata/%s' % (API_BASEURL, identifier)).json()
    location = {
        'dir': metadata['dir'],
        'server': metadata['server']
    }
    location = resolve_server(identifier)
    server = location['server']
    for f in metadata['files']:
        if f['name'].endswith('_djvu.xml'):
            path = location['dir'] + '/' + f['name']
            url = BOOK_OCR_URL % server
            r = requests.get(url, params={
                'path': path,
                'page': page,
                'callback': None,
                'mode': mode
            }, cookies=cookies)
            data = r.content.decode('utf-8')[14:-3]
            return json.loads(data)
    return {}

def search_wayback(query):
    url = "https://web-beta.archive.org/__wb/search/host?q="
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

def map_searchinside_to_iiif(identifier, q, idx=0):
    result = get_searchinside_data(identifier, q)
    if result['matches']:
        match = result['matches'][idx]['par'][0]

        # left, top, width, height
        width = (match['r'] - match['l'])
        height = (match['b'] - match['t'])
        url = '%s/%s$%s/%s,%s,%s,%s/full/0/default.jpg' % (
            iiif_url, identifier, match['page'],
            match['l'], match['t'], width, height
        )
        return requests.get(url, stream=True).content

def items(iid=None, query="", page=1, limit=100, fields="", sorts="",
          cursor=None, version=''):
    # aaron's idea: Weekly dump of ID of all identifiers (gzip)
    # elastic search query w/ paging
    if iid:
        return item(iid)
    # 'all:1' also works
    q = "NOT identifier:..*" + (" AND (%s)" % query if query else "")
    if version == 'v2':
        return scrape(query=q, fields=fields, sorts=sorts, count=limit,
                      cursor=cursor)
    return search(q, page=page, limit=limit)


def olpage_hack(archive_id):
    return requests.get('https://openlibrary.org/ia/%s' % archive_id,
                        allow_redirects=True, timeout=None).content

def get_olia_metadata(archive_id):
    return requests.get(OL_API % archive_id).json()


def item(iid):
    try:
        return requests.get('%s/metadata/%s' % (API_BASEURL, iid)).json()
    except ValueError as v:
        return v


def librivox(ocaid):
    """This API should be deprecated in favor of https://librivox.org/api/info"""
    from bs4 import BeautifulSoup
    metadata = item(ocaid)['metadata']
    desc = metadata['description']
    soup = BeautifulSoup(desc, 'html.parser')
    for a in soup.findAll('a'):
        if 'librivox.org/' in a['href'] and not a['href'].endswith('.org/'):
            return a['href']
    return None
    # html = requests.get(url).content
    # soup = BeautifulSoup(html, 'html.parser')
    # table = soup.findAll('table', {'class': 'metatable'})[0]


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


def scrape(query, fields="", sorts="", count=100, cursor="", security=True):
    """
    params:
        query: the query (using the same query Lucene-like queries supported by Internet Archive Advanced Search.
        fields: Metadata fields to return, comma delimited
        sorts: Fields to sort on, comma delimited (if identifier is specified, it must be last)
        count: Number of results to return (minimum of 100)
        cursor: A cursor, if any (otherwise, search starts at the beginning)
    """
    if not query:
        raise ValueError("GET 'query' parameters required")

    if int(count) > 1000 and security:
        raise MaxLimitException("Limit may not exceed 1000.")

    #sorts = sorts or 'date+asc,createdate'
    fields = fields or 'identifier,title'

    params = {
        'q': query
    }
    if sorts:
        params['sorts'] = sorts
    if fields:
        params['fields'] = fields
    if count:
        params['count'] = count
    if cursor:
        params['cursor'] = cursor

    r = requests.get(SCRAPE_API, params=params)
    return r.json()

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
    data = {
        "searchimg": "%s,%s" % (mime, base64img),
        "limit": "5",
        "search": "ia",
        "mode": "basic"
    }
    r = requests.post(REVERSE_IMAGE_SEARCH_URL, data=data)
    html = r.content
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.findAll('table', {'class': 'metatable'})[0]
        return [x.nextSibling.text for x in
                table.findAll('td', text="Identifier:")]
    except:
        return []
