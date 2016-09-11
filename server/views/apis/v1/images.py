#!/usr/bin/env python
#-*-coding: utf-8 -*-

"""
    images.py
    ~~~~~~~~~
    Reverse search for archive.org images

    :copyright: (c) 2015 by Internet Archive
    :license: see LICENSE for more details.
"""

import base64
from flask import Response, request, jsonify
from flask.views import MethodView
from views import rest_api, paginate
from api.archive import mimetype, download, reverse_image_search, \
    API_BASEURL, BOOK_DATA_URL

class ImageSearch(MethodView):
    @rest_api
    def post(self):
        img = request.files['img']
        base64img = base64.b64encode(img.read())
        return reverse_image_search(img.filename, base64img)

urls = (
    '', ImageSearch
    )
