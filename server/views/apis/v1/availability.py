#-*-coding: utf-8 -*-

"""
    availability.py
    ~~~~~~~~~~~~~~~
    URLs list for api.v1

    :copyright: (c) 2015 by Internet Archive
    :license: see LICENSE for more details.
"""

import os
import requests
from flask import Response, request
from flask.views import MethodView
from views import rest_api
from views.apis.v1 import wayback


class Endpoints(MethodView):
    @rest_api
    def get(self, uri=None):      
        urlbase = request.base_url
        return dict([(urls[i+1].__name__.split(".")[-1].lower(),
                      urlbase + urls[i])
                     for i in range(len(urls))[::2]])


class BooksAvailability(MethodView):
    @rest_api
    def get(self, uri=""):
        url = 'http://want.archive.org/api'
        if uri:
            url = os.path.join(url, uri)
        if request.query_string:
            url += '?%s' % request.query_string
        r = requests.get(url, stream=True, allow_redirects=True, timeout=None)
        return Response(r.content, mimetype=r.headers['content-type'])


class CDsAvailability(MethodView):
    def get(self, uri="lookupCD"):
        """
        Example: https://api.archivelab.org/v1/availability/cds?lengths=233.08+199.27&tollerance=0.2
        """
        url = 'http://dowewantit0.us.archive.org:5000/%s' % uri
        if request.query_string:
            url += '?%s' % request.query_string
        r = requests.get(url, stream=True, allow_redirects=True, timeout=None)
        return Response(r.content, mimetype="application/json")


urls = (
    '/wayback/<path:url>', wayback.Snapshots,
    '/wayback', wayback.Sources,
    '/books/<path:uri>', BooksAvailability,
    '/books', BooksAvailability,
    '/cds', CDsAvailability,
    '', Endpoints
    )
