#!/usr/bin/env python
#-*-coding: utf-8 -*-

"""
    __init__.py
    ~~~~~~~~~~~
    Auxiliary methods for rendering base template and partials for
    javascript frameworks, such as angular

    :copyright: (c) 2015 by Internet Archive
    :license: see LICENSE for more details.
"""

import sys
import json
from werkzeug import wrappers
from flask import render_template, Response, request
from flask.views import MethodView

class Base(MethodView):
    def get(self, uri=None):
        return render_template('base.html')

class Partial(MethodView):
    def get(self, partial):
        return render_template('partials/%s.html' % partial)

def paginate(page=1, limit=100):
    def outer(f):
        def inner(*args, **kwargs):
            _page = request.args.get('page', page)
            _limit = request.args.get('limit', limit)
            try:
                r = f(*args, page=_page, limit=_limit, **kwargs)['response']                
                r['ids'] = [d['identifier'] for d in r.pop('docs')]
                r['next'] = int(r['start']) + int(_limit)
            except Exception as e:
                r = {'error': str(e), 'ids': []}
            r['limit'] = int(_limit)
            r['page'] = int(_page)
            return r
        return inner
    return outer

def rest_api(f):
    """Decorator to allow routes to return json"""
    def inner(*args, **kwargs):
        try:
            try:
                res = f(*args, **kwargs)
                if isinstance(res, wrappers.Response):
                    return res
                response = Response(json.dumps(res))
            except Exception as e:
                response = Response(json.dumps({
                            "error": "%s: %s"
                            % (e.__class__.__name__, str(e))
                            }))

            response.headers.add('Content-Type', 'application/json')
            return response
        finally:
            #DB Rollbacks to protect against inconsistent states
            pass
    return inner
