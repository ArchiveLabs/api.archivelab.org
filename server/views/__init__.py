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
import calendar
from datetime import datetime
from flask import Response, request, jsonify
from flask.views import MethodView
from flask.json import JSONEncoder
from api.core import ApiException, HTTPException
from api import db

class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                if obj.utcoffset() is not None:
                    obj = obj - obj.utcoffset()
                    millis = int(
                        calendar.timegm(obj.timetuple()) * 1000 +
                        obj.microsecond / 1000
                    )
                    return millis
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

def paginate(page=1, limit=100):
    def outer(f):
        def inner(*args, **kwargs):
            _page = request.args.get('page', page)
            _limit = request.args.get('limit', limit)
            try:
                r = f(*args, page=_page, limit=_limit, **kwargs)
                if 'response' in r:
                    r = r['response']
                    r['ids'] = [d['identifier'] for d in r.pop('docs')]
                    r['next'] = int(r['start']) + int(_limit)
                    r['page'] = int(_page)
            except Exception as e:
                r = {'error': str(e), 'ids': []}
            r['limit'] = int(_limit)
            return r
        return inner
    return outer

def rest_api(f):
    """Decorator to allow routes to return json"""
    def inner(*args, **kwargs):
        try:
            return jsonify(f(*args, **kwargs))
        except Exception as e:
            return jsonify({"error": str(e)})
        finally:
            db.rollback()
            db.remove()
    return inner

def search(model, limit=50):
    query = request.args.get('query')
    field = request.args.get('field')
    limit = min(request.args.get('limit', limit), limit)
    if all([query, field, limit]):
        return model.search(query, field=field, limit=limit)
    raise ValueError('Query and field must be provided. Valid fields are: %s' \
                         %  model.__table__.columns.keys())
