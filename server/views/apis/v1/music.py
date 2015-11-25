#!/usr/bin/env python
#-*-coding: utf-8 -*-

"""
    music.py
    ~~~~~~~~
    Redirect /music requests through Groovebox API

    :copyright: (c) 2015 by Internet Archive
    :license: see LICENSE for more details.
"""

import requests
from flask import Response, request
from flask.views import MethodView


music_url = 'https://api.groovebox.org'


class Music(MethodView):
    def get(self, uri=""):
        url = '%s/%s' % (music_url, uri) if uri else music_url
        r = requests.get(url, stream=True)
        return Response(r.content, mimetype=r.headers['content-type'])


urls = (
    '/<path:uri>', Music,
    '/', Music,
    '', Music
)
