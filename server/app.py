#!/usr/bin/env python
#-*-coding: utf-8 -*-

"""
    app.py
    ~~~~~~
    The Archive.org API Server

    :copyright: (c) 2015 by Internet Archive
    :license: see LICENSE for more details.
"""

from flask import Flask
from flask.ext.routing import router
from flask.ext.cors import CORS
from views import apis
from configs import options, cors

urls = ('/v1', apis,
        '', apis)
app = router(Flask(__name__), urls)
cors = CORS(app) if cors else None

if __name__ == "__main__":
    app.run(**options)
