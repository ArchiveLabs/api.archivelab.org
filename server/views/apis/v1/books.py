#!/usr/bin/env python
#-*-coding: utf-8 -*-

"""
    books.py
    ~~~~~~~~
    Retrieve Archive.org book metadata

    :copyright: (c) 2015 by Internet Archive
    :license: see LICENSE for more details.
"""

from flask import Response, request, jsonify, render_template, send_file
from flask.views import MethodView
from sqlalchemy.orm.attributes import flag_modified
from views import rest_api, paginate
from api import books as api
from api.archive import item, items, mimetype, download, \
    get_book_data, get_book_page, get_book_iiif_manifest
from api.archive import search, fulltext_search, \
    map_searchinside_to_iiif, get_searchinside_data, get_wordsinside_data, \
    search_wayback, get_bookpage_ocr, get_bookpage_annotations, \
    get_book_annotations, get_toc, get_toc_page, get_book_fulltext
from configs import iiif_url


class BookMetadata(MethodView):
    @rest_api
    def get(self, archive_id):
        return item(archive_id)


class BookIIIFManifest(MethodView):
    @rest_api
    def get(self, archive_id=None):
        """Returns book metadata"""
        return get_book_iiif_manifest(archive_id, request.url_root)


class BookIAManifest(MethodView):
    def get(self, archive_id=None):
        """Returns book metadata"""
        return jsonify(get_book_data(archive_id))


class BookTOCManifest(MethodView):
    @rest_api
    def get(self, archive_id, page=None):
        """Test case: businessstatisti00blac"""
        toc_pages = get_toc(archive_id)
        return {'toc': toc_pages}

class BookTOC(MethodView):
    def get(self, archive_id, page=None):
        """Test case: businessstatisti00blac"""
        toc_page = get_toc_page(archive_id, page)
        return send_file(toc_page)

class BookPages(MethodView):
    @rest_api
    def get(self, archive_id):
        return {
            'pages': [page for page in get_book_data(archive_id)['leafNums']
                      if page]
        }


class BookPage(MethodView):
    def get(self, archive_id, page):
        r = get_book_page(archive_id, page, request.url_root)
        return Response(r.content, mimetype=r.headers['content-type'])

class Cite(MethodView):
    def get(self, archive_id=None):
        i = request.args
        q = i.get('q', '') or i.get('text', '')
        cite = i.get('cite', '')
        if cite:
            try:
                idx = int(cite)
            except ValueError:
                raise ValueError("cite must be int")
            return Response(
                map_searchinside_to_iiif(archive_id, q=q, idx=idx),
                mimetype="image/jpg")

class SearchInside(MethodView):
    @rest_api
    def get(self, archive_id=None):
        i = request.args
        q = i.get('q', '') or i.get('text', '')
        callback = i.get('callback', '')
        if q:
            return get_searchinside_data(archive_id, q=q, callback=callback)
        return get_wordsinside_data(archive_id, callback=callback)


class WordRegions(MethodView):
    @rest_api
    def get(self, archive_id, page):
        i = request.args
        mode = i.get('mode', 'paragraphs')
        return {'ocr': get_bookpage_ocr(archive_id, page, mode=mode)}

class BookText(MethodView):
    def get (self, archive_id):
        fulltext = get_book_fulltext(archive_id, stringio=True)
        filename = "%s_fulltext.txt" % archive_id
        if fulltext:
            return send_file(fulltext, mimetype='text/plain',
                             as_attachment=True, attachment_filename=filename)

class PageText(MethodView):
    def get(self, archive_id, page):
        pageocr = get_bookpage_ocr(archive_id, page)
        pagenum = request.args.get('page', '')
        plaintext = '\n'.join([block[0] for block in pageocr])
        if pagenum:
            plaintext = 'Page %s\n%s' % (page, plaintext)
        return Response(plaintext, mimetype='text/plain')

    @rest_api
    def post(self, archive_id, page):
        correction = request.json.get('correction')
        api.Ocr
        return {'correction': correction}

class PageAudio(MethodView):
    def get(self, archive_id, page):
        api.Audible.get(archive_id=archive_id, page_num=page)
        return Response("coming soon")

    @rest_api
    def post(self, archive_id, page):
        audible = request.json.get('audible')        
        return {'audible': audible}

class Annotations(MethodView):
    @rest_api
    def get(self, archive_id, page=None):
        crosslinks = request.args.get('crosslinks', None)
        if not page:
            return get_book_annotations(archive_id, crosslinks=crosslinks)
        return get_bookpage_annotations(archive_id, page)

class Endpoints(MethodView):
    @rest_api
    def get(self, uri=None):      
        urlbase = request.base_url
        return dict([(urls[i+1].__name__.split(".")[-1],
                      urlbase + urls[i])
                     for i in range(len(urls))[::2]])

urls = (
    '/<archive_id>/searchinside', SearchInside,
    '/<archive_id>/search', SearchInside,
    '/<archive_id>/cite', Cite,
    '/<archive_id>/pages/<page>/ocr', WordRegions,
    '/<archive_id>/pages/<page>/plaintext', PageText,
    '/<archive_id>/pages/<page>/audible', PageAudio,
    '/<archive_id>/pages/<page>/annotations', Annotations,
    '/<archive_id>/pages/<page>', BookPage,
    '/<archive_id>/pages', BookPages,
    '/<archive_id>/toc/<page>', BookTOC,
    '/<archive_id>/toc', BookTOCManifest,
    '/<archive_id>/fulltext', BookText,
    '/<archive_id>/annotations', Annotations,
    '/<archive_id>/iiif_manifest', BookIIIFManifest,
    '/<archive_id>/ia_manifest', BookIAManifest,
    '/<archive_id>', BookMetadata,
    '', Endpoints,
    )
