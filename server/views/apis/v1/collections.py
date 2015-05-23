#!/usr/bin/env python
#-*-coding: utf-8 -*-

"""
    snapshots.py
    ~~~~~~~~~~~~
    Archive.org collections API endpoints

    :copyright: (c) 2015 by Internet Archive
    :license: see LICENSE for more details.
"""

from flask import request
from flask.views import MethodView
from views import rest_api
from api import collections #, collection

class Collections(MethodView):
    @rest_api
    def get(self):
        return collections()

class Collection(MethodView):
    @rest_api
    def get(self, collection_id):
        #return collection(collection_id)
        return None

urls = (
    '/<collection_id>', Collection,
    '', Collections
)
