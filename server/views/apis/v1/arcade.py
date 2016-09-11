#!/usr/bin/env python
#-*-coding: utf-8 -*-

"""
    arcade.py
    ~~~~~~~~~
    Redirect /music requests through Groovebox API

    :copyright: (c) 2015 by Internet Archive
    :license: see LICENSE for more details.
"""

import requests
from flask import Response, request
from flask.views import MethodView
from api.archive import get_arcade_games
from views import rest_api


class Games(MethodView):
    @rest_api
    def get(self):
        i = request.args
        q = i.get('q', None)
        page = i.get('page', 1)
        return get_arcade_games(query=q, page=page)
        


urls = (
    '/', Games,
    '', Games
)
