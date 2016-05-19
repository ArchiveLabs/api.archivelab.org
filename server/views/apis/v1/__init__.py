#-*-coding: utf-8 -*-

"""
    __init__.py
    ~~~~~~~~~~~
    URLs list for api.v1

    :copyright: (c) 2015 by Internet Archive
    :license: see LICENSE for more details.
"""

import requests
from views import rest_api
from flask import Response, request
from flask.views import MethodView
from flask import request
from . import availability
from configs import API_BASEURL


class Endpoints(MethodView):
    @rest_api
    def get(self, uri=None):      
        urlbase = request.base_url[:-1]
        return dict([(urls[i+1].__name__.split(".")[-1].lower(),
                      urlbase + urls[i])
                     for i in range(len(urls))[::2]])


class Items(MethodView):
    @rest_api
    def get(self, uri=""):        
        url = 'http://archive.org/%s?%s' % ('/advancedsearch.php', request.query_string)
        r = requests.get(url, stream=True, allow_redirects=True, timeout=None)
        return Response(r.content, mimetype=r.headers['content-type'])


urls = (
    '/availability', availability,
    '/items', Items,
    '/', Endpoints,
    '', Endpoints
)
