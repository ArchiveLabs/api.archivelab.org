#!/usr/bin/env python
#-*-coding: utf-8 -*-

"""
    analytics.py
    ~~~~~~~~~~~
    A wrapper for Will's analytics framework

    :copyright: (c) 2015 by Internet Archive
    :license: see LICENSE for more details.
"""

import requests
from flask import Response, request, jsonify
from flask.views import MethodView
from views import rest_api, paginate


class Endpoints(MethodView):
    @rest_api
    def get(self, app=None):
        urlbase = request.url_root[:-1]
        return dict([(urls[i+1].__name__.split(".")[-1].lower(),
                      urlbase + urls[i])
                     for i in range(len(urls))[::2]])

class Apps(MethodView):
    def get(self, uri=""):
        pass

class App(MethodView):
    def get(self, uri=""):
        pass

urls = (
    '/apps/<app>', App,
    '/apps', Apps,
    '', Endpoints
)
