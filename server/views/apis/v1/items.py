#!/usr/bin/env python
#-*-coding: utf-8 -*-

"""
    items.py
    ~~~~~~~~
    Retrieve Archive.org items

    :copyright: (c) 2015 by Internet Archive
    :license: see LICENSE for more details.
"""

from flask import render_template
from flask.views import MethodView
from views import rest_api
from api import item

class Items(MethodView):
    @rest_api
    def get(self):
        return []

class Item(MethodView):
    @rest_api
    def get(self, iid):
        return item(iid)

class Metadata(MethodView):
    @rest_api
    def get(self, iid):
        items.get(iid)
        pass

class Reviews(MethodView):
    @rest_api
    def get(self):
        pass

class Files(MethodView):
    @rest_api
    def get(self):
        pass

class File(MethodView):
    def get(self):
        # set return type
        pass

urls = (
    '/<iid>/metadata', Metadata,
    '/<iid>/reviews', Reviews,
    '/<iid>/files/:filename', File,
    '/<iid>/files', Files,
    '/<iid>', Item,
    '', Items
    )
