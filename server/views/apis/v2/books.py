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
    get_book_data


class Books(MethodView):
    @rest_api
    def get(self, page=1, limit=100):
        filters = request.args.get('filters', '')
        fs = "mediatype:(texts)" + " AND (%s)" % filters if filters else ""
        return items(page=page, limit=limit, filters=fs)


class Book(MethodView):
    def get(self, identifier):
        """Returns book metadata"""
        return jsonify(get_book_data(identifier))


urls = (
    '/<identifier>', Book,
    '', Books
    )
