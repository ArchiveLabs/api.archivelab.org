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
from api import items
from configs import pragma_url


class Pragma(MethodView):
    def get(self, uri=""):
        url = '%s/%s' % (pragma_url, uri) if uri else pragma_url
        r = requests.get(url, stream=True, allow_redirects=True, timeout=None)
        return Response(r.content, mimetype=r.headers['content-type'])


urls = (
    '/<path:uri>', Pragma,
    '', Pragma
)
