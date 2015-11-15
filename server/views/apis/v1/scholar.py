#!/usr/bin/env python
#-*-coding: utf-8 -*-

"""
    scholar.py
    ~~~~~~~~~~
    Redirects requests to scholar.archive.org service

    :copyright: (c) 2015 by Internet Archive
    :license: see LICENSE for more details.
"""

import requests
from flask import Response, request, jsonify
from flask.views import MethodView
from views import rest_api, paginate
from api import items

metapub_url = 'http://api.archivelab.org:8080'


class Journals(MethodView):
    @rest_api
    def get(self, uri=""):
        url = '%s/%s' % (metapub_url, uri) if uri else metapub_url
        r = requests.get(url, stream=True)
        return Response(r.content, mimetype=r.headers['content-type'])


urls = (
    '/<path:uri>', Journals,
    '', Journals
)
