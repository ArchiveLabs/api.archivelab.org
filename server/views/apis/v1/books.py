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
from views import rest_api, paginate
from api import books as api
from api.archive import item, items, mimetype, download, \
    get_book_data



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


class Authors(MethodView):
    @rest_api
    def get(self, aid=None):
        if aid:
            return api.Author.get(aid).dict(books=True)
        return {
            'authors': [author.dict(books=True) for author in
                        api.Author.all()]
        }


class Sequences(MethodView):
    @rest_api
    def get(self):
        return {
            'sequences': [s.dict() for s in api.Sequence.all()]
        }


class Books(MethodView):
    @rest_api
    def get(self, archive_id=None):
        try:
            if archive_id:
                return api.Book.get(archive_id=archive_id).dict()
            return {
                'book': [book.dict() for book in 
                         api.Book.all()]
            }
        except Exception:
            return item(archive_id)


class BookData(MethodView):
    def get(self, archive_id=None):
        """Returns book metadata"""
        return jsonify(get_book_data(archive_id))


class Admin(MethodView):
    def get(self):
        authors = sorted([a.dict(names=True, books=True)
                          for a in api.Author.all()],
                         key=lambda a: a['id'], reverse=True)
        books = sorted([b.dict() for b in api.Book.all()],
                       key=lambda b: b['id'], reverse=True)
        seqs = [s.dict() for s in api.Sequence.all()]
        return render_template(
            'admin.html', authors=authors, books=books, seqs=seqs)


class SequencesPage(MethodView):

    def get(self, sid=None):
        if sid:
            return render_template('sequence.html', sequence=api.Sequence.get(sid))
        sequences = [s.dict() for s in api.Sequence.all()]
        return render_template('sequences.html', sequences=sequences, len=len)


    def post(self):
        pass


class AuthorPage(MethodView):

    def get(self, aid=None):
        if aid:
            return render_template('author.html', author=api.Author.get(aid))
        authors = [author.dict(books=True) for author in api.Author.all()]
        return render_template('authors.html', authors=authors, len=len)

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
            book_ids = [int(b) for b in i.get('bids', None).replace(' ', '').split(',')]
            for bid in book_ids:
                a.books.append(api.Book.get(bid))
            a.save()
        return a.dict()




class BookPage(MethodView):
    def get(self, archive_id):
        # get all sequences containing this book
        ## get all books following this book in a sequence
        # get all collections containing this book

        book = api.Book.get(archive_id=archive_id)
        author_ids = ', '.join(str(int(a.id)) for a in book.authors)
        return render_template(
            'book.html', book=book, aids=author_ids)

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


urls = (
    '/collections/<cid>', Collection,
    '/collections', Collections,
    '/authors/<aid>', Authors,
    '/authors', Authors,
    '/sequences', Sequences,
    '/admin', Admin,
    '/b/<archive_id>', BookPage,
    '/a/<aid>', AuthorPage,
    '/a', AuthorPage,
    '/s', SequencesPage,
    '/b', BookPage,
    #'/<archive_id>/ocr', Ocr,
    '/<archive_id>/metadata', BookData,
    '/<archive_id>', Books,
    '', Books
    )
