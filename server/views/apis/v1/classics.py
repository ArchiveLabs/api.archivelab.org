#!/usr/bin/env python
#-*-coding: utf-8 -*-

"""
    books.py
    ~~~~~~~~
    Retrieve Archive.org book metadata

    :copyright: (c) 2015 by Internet Archive
    :license: see LICENSE for more details.
"""

from flask import Response, request, jsonify, render_template
from flask.views import MethodView
from sqlalchemy.orm.attributes import flag_modified
from views import rest_api, paginate, search
from api.archive import olpage_hack
from api import books as api


class Collections(MethodView):
    @rest_api
    def get(self, cid=None):
        if cid:
            return api.Collection.get(cid).dict(books=True)
        return {
            'collections': [c.dict() for c in api.Collection.all()]
        }


class Collection(MethodView):
    @rest_api
    def get(self, cid):
        collection = api.Collection.get(cid)
        return collection.dict(books=True, collections=True)


class Sequences(MethodView):
    @rest_api
    def get(self):
        return {
            'sequences': [s.dict() for s in api.Sequence.all()]
        }

class Sequence(MethodView):

    def get(self, sid=None):
        if sid:
            return render_template('sequence.html', sequence=api.Sequence.get(sid))
        sequences = [s.dict() for s in api.Sequence.all()]
        return render_template('sequences.html', sequences=sequences, len=len)


    def post(self):
        pass


class Author(MethodView):

    @rest_api
    def get(self, aid=None):        
        return api.Author.get(id=aid).dict()


class Authors(MethodView):

    @rest_api
    def get(self):
        return {
            'authors': sorted([author.dict(names=True, books=True) for author in
                               api.Author.all()], key=lambda a: a['id'], reverse=True)
        }

    @rest_api
    def post(self):
        i = request.form
        olid = i.get('olid')
        name = i.get('name')

        try:
            a = api.Author.get(name=name)
            a.olid = olid
        except:
            a = api.Author(name=name, olid=olid)
            a.create()

        aka = i.get('aka')
        if aka:
            for alias in aka.split(','):
                an = api.AuthorName(name=alias.strip(), author_id=a.id)
                an.create()
                a.names.append(an)
            a.save()                

        book_ids = i.get('bids')
        if book_ids:
            book_ids = [int(b) for b in
                        i.get('bids', None).replace(' ', '').split(',')]
            for bid in book_ids:
                a.books.append(api.Book.get(bid))
            a.save()
        return a.dict()

class Book(MethodView):
    @rest_api
    def get(self, archive_id):
        return api.Book.get(archive_id=archive_id).dict()


class Books(MethodView):
    @rest_api
    def get(self):
        if request.args.get('action') == 'search':
            return {'books': [b.dict() for b in search(api.Book)]}
        return {
            'books': [book.dict() for book in 
                     api.Book.all()]
        }

    @rest_api
    def post(self, archive_id=None):
        i = request.form
        if i.get('method') == "delete" and archive_id:
            return self.delete(archive_id)

        archive_id = i.get('archive_id')
        name = i.get('name')
        desc = i.get('description')

        try:
            b = api.Book.get(archive_id=archive_id)
        except:
            b = api.Book(archive_id=archive_id)
            b.create()

        author_ids = i.get('aids')
        if author_ids:
            author_ids = [a.strip() for a in author_ids.split(',')]
            for aid in author_ids:
                b.authors.append(api.Author.get(aid))

        collection_ids = i.get('cids')
        if collection_ids:
            cids = [int(c.strip()) for c in collection_ids.split(',')]
            for cid in cids:
                b.collections.append(api.Collection.get(cid))
                
        if name:
            b.name = name

        if desc:
            b.data[u'description'] = desc
            flag_modified(b, 'data')

        b.save()

        return b.dict()

    @rest_api
    def delete(self, archive_id):
        i = request.form
        try:
            b = api.Book.get(archive_id=archive_id)
            b.remove()
        except:
            return

class Endpoints(MethodView):
    @rest_api
    def get(self, uri=None):      
        urlbase = request.base_url[:-1]
        return dict([(urls[i+1].__name__.split(".")[-1],
                      urlbase + urls[i])
                     for i in range(len(urls))[::2]])

urls = (
    '/collections/<cid>', Collection,
    '/collections', Collections,

    '/<sid>', Sequence,
    '/sequences', Sequences,

    '/authors/<aid>', Author,
    '/authors', Authors,

    '/books/<archive_id>', Book,
    '/books', Books,

    '', Endpoints
    )
