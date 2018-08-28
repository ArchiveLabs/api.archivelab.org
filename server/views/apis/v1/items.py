#!/usr/bin/env python
#-*-coding: utf-8 -*-

"""
    items.py
    ~~~~~~~~
    Retrieve Archive.org items

    :copyright: (c) 2015 by Internet Archive
    :license: see LICENSE for more details.
"""

import internetarchive as ia
from flask import render_template, Response, request, jsonify
from flask.views import MethodView
from views import rest_api, paginate
from api.archive import item, items, mimetype, download

class Items(MethodView):
    @rest_api
    @paginate()
    def get(self, page=1, limit=100):
        query = request.args.get('filters', '')
        query = request.args.get('q', '')
        fields = request.args.get('fields', '')
        sorts = request.args.get('sorts', '')
        cursor = request.args.get('cursor', '')
        version = request.args.get('v', '')
        return items(page=page, limit=limit, fields=fields, sorts=sorts,
                     query=query, cursor=cursor, version=version)

    @rest_api
    def post(self):
        """For Upload API"""
        # f = request.files['file']
        # ia.upload(name, f)
        return item(iid)


class Item(MethodView):
    @rest_api
    def get(self, iid):
        return item(iid)


class Metadata(MethodView):
    @rest_api
    def get(self, iid):
        return item(iid)['metadata']


class Reviews(MethodView):
    @rest_api
    def get(self, iid):
        return item(iid)['reviews']


class Files(MethodView):
    @rest_api
    def get(self, iid):
        return item(iid)['files']


class File(MethodView):
    def get(self, iid, filename):
        """Download the specified file"""
        r = download(iid, filename, headers=request.headers)
        return Response(r.iter_content(chunk_size=1024),
                        headers=dict(r.headers),
                        status=r.status_code,
                        mimetype=mimetype(filename))

class Manifests(MethodView):
    def get(self, iid, manifest=None):
        metadata = item(iid)['metadata']
        if manifest:
            return jsonify({})
        result = {

        }
        if 'librivoxaudio' in metadata.get('collection', []):
            result['opds_audio'] = request.url_root + 'books/%s/opds_audio_manifest' % (iid)

        if metadata.get('mediatype') == 'texts':
            result['iiif'] = request.url_root + 'iiif/%s/manifest.json' % (iid)
            result['ia_book'] = request.url_root + 'books/%s/ia_manifest' % (iid)
            result['opds'] = 'https://bookserver.archive.org/catalog/%s' % (iid)

        return jsonify(result)


urls = (
    '/<iid>/manifests', Manifests,
    '/<iid>/metadata', Metadata,
    '/<iid>/reviews', Reviews,
    '/<iid>/files/<path:filename>', File,
    '/<iid>/files', Files,
    '/<iid>', Item,
    '', Items
    )
