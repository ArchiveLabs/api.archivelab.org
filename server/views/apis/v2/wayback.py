#!/usr/bin/env python
#-*-coding: utf-8 -*-

"""
    snapshots.py
    ~~~~~~~~~~~~
    Wayback machine API endpoints

    :copyright: (c) 2015 by Internet Archive
    :license: see LICENSE for more details.
"""

from flask import request
from flask.views import MethodView
from api import snapshot
from views import rest_api

class Wayback(MethodView):
    @rest_api
    def get(self):
        raise NotImplementedError("List of all wayback snapshots, " \
                                      "alphabetized by domain")

class Snapshots(MethodView):
    @rest_api
    def get(self, url):
        i = request.args
        ts = i.get('timestamp', None)
        return snapshot(url, timestamp=ts)

urls = (
    '/<path:url>', Snapshots,
    '', Wayback
)
