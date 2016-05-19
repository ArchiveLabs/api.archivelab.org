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
from bs4 import BeautifulSoup

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
                               "%20AND%20%3C" + d2 + "&mode=more"
        #r = requests.get(url)
        #soup = BeautifulSoup(r.content)
        #res = soup.findAll('div', {'class': 'infoBarDiv'})
        #return res[0]


class Snapshots(MethodView):
    @rest_api
    def get(self, url):
        i = request.args
        ts = i.get('timestamp', None)
        return snapshot(url, timestamp=ts)

class Sources(MethodView):
    @rest_api
    def get(self):
        return {
            "captures": "null",
            "hosts": "null",
            "docs": [
                "http://wwwb-front1.us.archive.org:8085/usage",
                "https://archive.org/help/wayback_api.php"
            ]
        }

urls = (
    '/stats', Stats,
    '/<path:url>', Snapshots,
    '', Wayback
)
