#!/usr/bin/env python
#-*-coding: utf-8 -*-

"""
    search.py
    ~~~~~~~~~
    Archive.org Search API endpoints

    :copyright: (c) 2015 by Internet Archive
    :license: see LICENSE for more details.
"""

from flask import render_template, request
from flask.views import MethodView
from views import rest_api
from api import books as api
from api.archive import search, fulltext_search, \
    get_searchinside_data, get_wordsinside_data, search_wayback, \
    item, librivox


class Search(MethodView):
    @rest_api
    def get(self):
        i = request.args
        query = i.get('q', '')
        limit = i.get('limit', 50)
        page = i.get('page', 1)
        sort = i.get('sort', None)
        fields = i.get('fields', None)
        return search(query, page=page, limit=limit, sort=sort, fields=fields)


class Librivox(MethodView):
    @rest_api
    def get(self, ocaid=None):
        return {'url': librivox(ocaid)}


class FulltextSearch(MethodView):
    @rest_api
    def get(self):
        i = request.args
        fields = [f.strip() for f in i.get('fields', '').split(',')]
        names = 'names' in fields
        ids = 'ids' in fields
        hits = 'hits' in fields
        text = i.get('q', '') or i.get('text', '') or i.get('search', '')

        return fulltext_search(text, collection=i.get('collection'),
                               ids=ids, names=names, hits=hits)

class SearchInside(MethodView):
    @rest_api
    def get(self, bid=None):
        i = request.args
        q = i.get('q', '') or i.get('text', '')
        callback = i.get('callback', '')
        if q:
            return get_searchinside_data(bid, q=q, callback=callback)
        return get_wordsinside_data(bid, callback=callback)


class FulltextSearchClassics(MethodView):

    @rest_api
    def get(self):
        query = request.args.get('q')
        page = request.args.get('page', 0)
        limit = int(request.args.get('limit', 0))

        return api.search_all(query, page=page, limit=limit)


class WaybackSearch(MethodView):

    @rest_api
    def get(self):
        query = request.args.get('q')
        return {'matches': search_wayback(query)}


urls = (
    '/books/<bid>/regions', SearchInside,
    '/books/<bid>', SearchInside,
    '/books', FulltextSearch,
    '/librivox/<ocaid>', Librivox,
    '/classics', FulltextSearchClassics,
    '/wayback', WaybackSearch,
    '', Search
)
