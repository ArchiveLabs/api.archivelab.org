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
from api.archive import items

metapub_url = 'https://scholar.archivelab.org'


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
