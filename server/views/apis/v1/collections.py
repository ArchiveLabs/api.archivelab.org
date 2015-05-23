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
from views import rest_api
import items
from api import collections #, collection

class Collections(MethodView):
    @rest_api
    def get(self):
        return collections()

class Collection(MethodView):
    @rest_api
    def get(self, collection_id):
        return collections(collection_id=collection_id)

class Item(MethodView):
    def get(self, collection_id, iid):
        return redirect('/items/%s' % iid)

urls = (
    '/<collection_id>/<iid>', Item,
    '/<collection_id>', Collection,
    '', Collections
)
