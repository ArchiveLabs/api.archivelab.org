
#!/usr/bin/env python
#-*-coding: utf-8 -*-

"""
    snapshots.py
    ~~~~~~~~~~~~
    Wayback machine API endpoints

    :copyright: (c) 2015 by Internet Archive
    :license: see LICENSE for more details.
"""

from flask import Flask
from flask import render_template, request
from flask.views import MethodView
import requests

class Search(MethodView):
    def GET(self):
        i = request.args
        #http://web.archive.org/web/timemap/link/{URI-R}
        #http://web.archive.org/web/{URI-R}
        return requests.get("http://archive.org/wayback/available?url=" 
                            + i.get('url', '')).json
