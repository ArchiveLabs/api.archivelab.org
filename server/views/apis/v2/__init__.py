#-*-coding: utf-8 -*-

"""
    __init__.py
    ~~~~~~~~~~~
    URLs list for api.v1

    :copyright: (c) 2015 by Internet Archive
    :license: see LICENSE for more details.
"""

from flask import request
from flask.views import MethodView
from views import rest_api
from views.apis.v1 import availability, wayback
from views.apis.v2 import items, collections, search, iiif, pragma, \
    music, books, analytics, television, scholar, webtorrent, \
    images


class Endpoints(MethodView):
    @rest_api
    def get(self, uri=None):      
        urlbase = request.base_url[:-1]
        return dict([(urls[i+1].__name__.split(".")[-1].lower(),
                      urlbase + urls[i])
                     for i in range(len(urls))[::2]])


urls = (
    '/items', items,
    '/search', search.Search,
    '/collections', collections,
    '/wayback', wayback,
    '/music', music,
    '/images', images,
    '/iiif', iiif,
    '/pragma', pragma,
    '/scholar', scholar,
    '/books', books,
    '/analytics', analytics,
    #'/television', television,
    '/webtorrents', webtorrent,
    '/availability', availability,
    '/', Endpoints
)
