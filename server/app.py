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
from views import apis
from views.apis.v1 import items
from configs import options

urls = ('', apis)
app = router(Flask(__name__), urls)

if __name__ == "__main__":
    app.run(**options)
