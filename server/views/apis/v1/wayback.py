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
from api.archive import wayback_snapshot, wayback_search
from views import rest_api


class Wayback(MethodView):
    @rest_api
    def get(self):
        raise NotImplementedError("List of all wayback snapshots, " \
                                      "alphabetized by domain")

class Stats(MethodView):
    @rest_api
    def get(self):
        d1, d2 = request.args.get('date', ':').split(':')
        c = request.args.get('collection', '*;widecrawl*')
        url = "https://archive.org/metamgr.php?&w_mediatype=web" \
              "&w_collection=" + c + "&w_publicdate=%3E" + d1 + \
                               "%20AND%20%3C" + d2 + "&mode=more&output_format=json"
        r = requests.get(url)
        data = r.json()
        return data

class Snapshots(MethodView):
    @rest_api
    def get(self, url):
        i = request.args
        ts = i.get('timestamp', None)
        return wayback_snapshot(url, timestamp=ts)


class Search(MethodView):
    @rest_api
    def get(self):
        i = request.args
        q = i.get('q', '')
        return wayback_search(q)



class Sources(MethodView):
    @rest_api
    def get(self):
        return {}


urls = (
    '/stats', Stats,
    '/search', Search,
    '/<path:url>', Snapshots,
    '', Wayback
)
