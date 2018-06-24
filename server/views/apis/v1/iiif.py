#!/usr/bin/env python
#-*-coding: utf-8 -*-

"""
    iiif.py
    ~~~~~~~~
    Redirect requests for IIIF resources through iiif.archive.org

    :copyright: (c) 2015 by Internet Archive
    :license: see LICENSE for more details.
"""

import requests
from flask import Response, request, jsonify
from flask.views import MethodView
from views import rest_api, paginate
from api.archive import items
from configs import iiif_url


class Catalog(MethodView):
    @rest_api
    @paginate()
    def get(self, page=1, limit=1000):
        q = request.args.get('q', '')
        query = "(mediatype:(texts) OR mediatype:(image))" + \
                ((" AND %s" % q) if q else "")
        fields = request.args.get('fields', '')
        sorts = request.args.get('sorts', '')
        cursor = request.args.get('cursor', '')
        version = 'v2'
        limit = 1000
        return items(page=page, limit=limit, fields=fields, sorts=sorts,
                     query=query, cursor=cursor, version=version)

class IIIF(MethodView):
    def get(self, uri=""):
        url = '%s/%s' % (iiif_url, uri) if uri else iiif_url
        r = requests.get(url, params={'domain': '%siiif/' % request.url_root}, stream=True,
                         allow_redirects=True, timeout=None)
        return Response(r.content, mimetype=r.headers['content-type'])


urls = (
    '/<path:uri>', IIIF,
    '', Catalog
)
