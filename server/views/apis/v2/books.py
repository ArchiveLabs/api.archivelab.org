#!/usr/bin/env python
#-*-coding: utf-8 -*-

"""
    books.py
    ~~~~~~~~
    Retrieve Archive.org book metadata

    :copyright: (c) 2015 by Internet Archive
    :license: see LICENSE for more details.
"""

from flask import Response, request, jsonify
from flask.views import MethodView
from views import rest_api, paginate
from api import item, items, mimetype, download, \
    API_BASEURL, BOOK_DATA_URL


class Books(MethodView):
    @rest_api
    def get(self, page=1, limit=100):
        filters = request.args.get('filters', '')
        fs = "mediatype:(texts)" + " AND (%s)" % filters if filters else ""
        return items(page=page, limit=limit, filters=fs)


class Book(MethodView):
    def get(self, identifier):
        """Returns book metadata"""
        metadata = requests.get(
            '%s/metadata/%s' % (API_BASEURL, identifier)).json()
        subPrefix = metadata['dir']
        server = metadata.get('server', API_BASEURL)
        r = requests.get(BOOK_DATA_URL % server, params={
            'server': server,
            'itemPath': subPrefix,
            'itemId': identifier
        })
        data = r.json()
        return jsonify(data)


urls = (
    '/<iid>', Book,
    '', Books
    )
