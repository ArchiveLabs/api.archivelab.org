#!/usr/bin/env python
#-*-coding: utf-8 -*-

"""
    snapshots.py
    ~~~~~~~~~~~~
    Archive.org collections API endpoints

    :copyright: (c) 2015 by Internet Archive
    :license: see LICENSE for more details.
"""

from flask import request, redirect
from flask.views import MethodView
from views import rest_api, paginate
from api import collections

class Collections(MethodView):

    @rest_api
    @paginate()
    def get(self, page=1, limit=100):
        return collections(page=page, limit=limit)

class Collection(MethodView):
    @rest_api
    @paginate(limit=1000)
    def get(self, collection_id, page=1, limit=100):
        return collections(collection_id=collection_id,
                           page=page, limit=limit, security=False)

class Item(MethodView):
    def get(self, collection_id, iid):
        return redirect('/items/%s' % iid)

urls = (
    '/<collection_id>/<iid>', Item,
    '/<collection_id>', Collection,
    '', Collections
)
