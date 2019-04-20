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
from flask import render_template, Response, request, jsonify, redirect
from flask.views import MethodView
from views import rest_api, paginate
from api.archive import item, items, mimetype, download, resolve_server
from configs import API_BASEURL

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

class Generate(MethodView):
    def get(self, iid, fmt=None):
        bd = resolve_server(iid)['metadata']
        encrypt = bool(int(request.args.get('encrypt', 0)))
        reCache = bool(int(request.args.get('reCache', 0)))
        metadata = bd['metadata']
        files = bd.get('files')
        if bd and fmt in ['epub', 'daisy', 'mobi']:
            if metadata['mediatype'] == 'texts':
                doc = next(f['name'].replace('_abbyy.gz', '')
                           for f in files
                           if f['name'].endswith('_abbyy.gz'))
                url = 'https://%s/epub/index.php?id=%s&dir=%s&doc=%s&type=%s&debug=1' % (
                    bd['server'], iid, bd['dir'], doc, fmt)
                if reCache:
                    url += "&reCache=1"
                if not encrypt:
                    url += "&skipenc=1"
                return redirect(url)
        return jsonify({"error": "invalid fmt %s" % bd})

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
        data = jsonify(result)
        print(dir(data))
        return data


urls = (
    '/<iid>/manifests', Manifests,
    '/<iid>/metadata', Metadata,
    '/<iid>/reviews', Reviews,
    '/<iid>/files/<path:filename>', File,
    '/<iid>/files', Files,
    '/<iid>/generate/<fmt>', Generate,
    '/<iid>', Item,
    '', Items
    )
