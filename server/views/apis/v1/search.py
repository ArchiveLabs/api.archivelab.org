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
from api import search

class Search(MethodView):
    @rest_api
    def get(self):
        i = request.args
        query = i.get('q', '')
        limit = i.get('limit', 50)
        page = i.get('page', 1)
        return search(query, page=page, limit=limit)
