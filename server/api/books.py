#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    api/books.py
    ~~~~~~~~~~~~~
    Pragma API

    :copyright: (c) 2015 by mek.
    :license: see LICENSE for more details.
"""

from random import randint
from datetime import datetime
import requests
import internetarchive as ia
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import Column, Unicode, BigInteger, Integer, \
    Unicode, DateTime, ForeignKey, Table, exists, func
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm.exc import ObjectDeletedError
from sqlalchemy.orm import relationship
from api import db, engine, core


FULLTEXT_SEARCH_API = "https://api.archivelab.org/search/books"


def fulltext_search(text, collection='greekclassicslist'):
    url = FULLTEXT_SEARCH_API + '?text=%s' % text
    if collection:
        url += '&collection=%s' % collection
    r = requests.get(url)
    return r.json()


collections_collections = Table(
    'collections_collections', core.Base.metadata,
    Column('id', BigInteger, primary_key=True),
    Column('parent_id', BigInteger, ForeignKey('collections.id'), nullable=False),
    Column('child_id', BigInteger, ForeignKey('collections.id'), nullable=False),
    Column('created', DateTime(timezone=False), default=datetime.utcnow,
           nullable=False)
)


book_collections = Table(
    'book_collections', core.Base.metadata,
    Column('id', BigInteger, primary_key=True),       
    Column('collection_id', BigInteger, ForeignKey('collections.id'), nullable=False),
    Column('book_id', BigInteger, ForeignKey('books.id'), nullable=False),
    Column('created', DateTime(timezone=False), default=datetime.utcnow,
           nullable=False)
)

book_authors = Table(
    'book_authors', core.Base.metadata,
    Column('id', BigInteger, primary_key=True),       
    Column('author_id', BigInteger, ForeignKey('authors.id'), nullable=False),
    Column('book_id', BigInteger, ForeignKey('books.id'), nullable=False),
    Column('role', Unicode),  # author? translator?
    Column('created', DateTime(timezone=False), default=datetime.utcnow,
           nullable=False)
)

book_sequences = Table(
    'book_sequences', core.Base.metadata,
    Column('id', BigInteger, primary_key=True),       
    Column('sequence_id', BigInteger, ForeignKey('sequences.id'), nullable=False),
    Column('book_id', BigInteger, ForeignKey('books.id'), nullable=False),
    Column('created', DateTime(timezone=False), default=datetime.utcnow,
           nullable=False)
)

book_remote_ids = Table(
    'book_remote_ids', core.Base.metadata,
    Column('id', BigInteger, primary_key=True),       
    Column('book_id', BigInteger, ForeignKey('books.id'), nullable=False),
    Column('remote_id', BigInteger, ForeignKey('remote_ids.id'), nullable=False),
    Column('created', DateTime(timezone=False), default=datetime.utcnow,
           nullable=False)
)

author_remote_ids = Table(
    'author_remote_ids', core.Base.metadata,
    Column('id', BigInteger, primary_key=True),
    Column('author_id', BigInteger, ForeignKey('authors.id'), nullable=False),
    Column('remote_id', BigInteger, ForeignKey('remote_ids.id'), nullable=False),
    Column('created', DateTime(timezone=False), default=datetime.utcnow,
           nullable=False)
)

class RemoteId(core.Base):

    __tablename__ = "remote_ids"

    id = Column(BigInteger, primary_key=True)    
    source_id = Column(BigInteger, ForeignKey('sources.id'), nullable=False)
    remote_id = Column(Unicode, nullable=False, unique=True)


class Source(core.Base):

    SOURCE_IDS = {
        "wikidata": "https://www.wikidata.org",
        "openlibrary": "https://openlibrary.org",
        "wikipedia": "https://en.wikipedia.org",
        "librarything": "https://www.librarything.com",
        "goodreads": "https://www.goodreads.com",
        "worldcat": "https://www.worldcat.org/",
        "googlebooks": "https://books.google.com/"
    }

    __tablename__ = "sources"

    id = Column(BigInteger, primary_key=True)
    url = Column(Unicode, nullable=False, unique=True)
    name = Column(Unicode, nullable=False, unique=True)


class Collection(core.Base):

    __tablename__ = "collections"

    id = Column(BigInteger, primary_key=True)
    name = Column(Unicode, nullable=False, unique=True)
    data = Column(JSON)
    history = Column(JSON) 
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)

    books = relationship('Book', secondary=book_collections, backref="collections")
    subcollections = relationship('Collection', secondary=collections_collections,
                                  primaryjoin=id==collections_collections.c.parent_id,
                                  secondaryjoin=id==collections_collections.c.child_id,
                                  backref="parents")


    def add_book(self, archive_id):
        if not archive_id:
            raise ValueError("valid archive_id must be provided")
        try:
            b = Book.get(archive_id=archive_id)
        except:
            b = Book(archive_id=archive_id)
            b.create()
        self.books.append(b)
        self.save()


    def dict(self, books=False, collections=False):
        co = super(Collection, self).dict()
        if books:
            co['books'] = [b.dict(minimal=True) for b in self.books]
        if collections:
            co['subcollections'] = [sc.dict() for sc in self.subcollections]
        return co


class Author(core.Base):

    __tablename__ = "authors"

    id = Column(BigInteger, primary_key=True)
    olid = Column(Unicode, nullable=False, unique=True)  # openlibrary
    name = Column(Unicode, nullable=False)
    data = Column(JSON)
    history = Column(JSON) 
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)

    books = relationship('Book', secondary=book_authors, backref="authors")
    remote_ids = relationship('RemoteId', secondary=author_remote_ids, backref="authors")

    def dict(self, names=False, books=False):
        author = super(Author, self).dict()
        data = author.pop('data')
        author['name'] = self.name
        if data:
            if data.get('years'):
                author['years'] = data['years']
            if data.get('languages'):
                author['languages'] = data['languages']
        author['remote_ids'] = [rid.dict() for rid in self.remote_ids]
        author['created'] = author['created'].ctime()
        if books:
            author['books'] = [book.dict(minimal=True) for book in self.books]
        if names:
            author['names'] = [an.name for an in self.names]
        return author


    def add_remote_ids(self, **rids):
        for source, rid in rids.items():
            rid = RemoteId(source_id=Source.get(name=source).id, remote_id=rid)
            rid.create()
            self.remote_ids.append(rid)
        self.save()
        return self.remote_ids


class AuthorName(core.Base):

    __tablename__ = "author_names"

    id = Column(BigInteger, primary_key=True)
    author_id = Column(BigInteger, ForeignKey('authors.id'), nullable=False)
    name = Column(Unicode)

    author = relationship('Author', foreign_keys=[author_id], backref="names",
                          primaryjoin="AuthorName.author_id==Author.id")

class Ocr(core.Base):

    __tablename__ = "corrections"

    id = Column(BigInteger, primary_key=True)
    archive_id = Column(Unicode, nullable=False)
    page_num = Column(Integer, nullable=False)
    page_text = Column(Unicode, nullable=False, unique=True)
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)

class Audible(core.Base):

    __tablename__ = "audibles"

    """Create an audible archive.org user, create an audible item for each book w/ the audio files"""

    id = Column(BigInteger, primary_key=True)
    archive_id = Column(Unicode, nullable=False)
    page_num = Column(Integer, nullable=False)
    recording_url = Column(Unicode, nullable=False)
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)

class Book(core.Base):

    __tablename__ = "books"

    id = Column(BigInteger, primary_key=True)
    archive_id = Column(Unicode, nullable=False, unique=True)
    name = Column(Unicode)
    cover_url = Column(Unicode)
    data = Column(JSON)
    history = Column(JSON) 
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)

    remote_ids = relationship('RemoteId', secondary=book_remote_ids, backref="books")


    def create_pre_hook(self):
        self.data = ia.get_item(self.archive_id).metadata
        self.name = self.data.get('title')
        #self.data.update(get_olia_metadata(self.archive_id))
        self.cover_url = 'https://archive.org/services/img/' + self.archive_id


    def add_metadata(self, d):
        self.data.update(d)
        flag_modified(self, 'data')
        

    def dict(self, minimal=False):
        book = super(Book, self).dict()
        book['manifest'] = 'https://iiif.archivelab.org/%s/manifest.json' % self.archive_id
        book['authors'] = [a.dict() for a in self.authors]
        book['collections'] = [(c.id, c.name) for c in self.collections]
        book['sequences'] = [s.name for s in self.sequences]
        book['created'] = book['created'].ctime()
        if minimal:
            del book['data']
        return book


class Sequence(core.Base):

    """TODO: Create custom IIIF manifests based on the information inside
    `data` json"""

    __tablename__ = "sequences"

    id = Column(BigInteger, primary_key=True)
    name = Column(Unicode, unique=True)
    order = Column(JSON)  # Order of books in sequence
    data = Column(JSON)
    history = Column(JSON) 
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)

    books = relationship('Book', secondary=book_sequences,
                         backref="sequences")

    def dict(self):
        seq = super(Sequence, self).dict()
        seq['books'] = [book.dict() for book in self.books]
        return seq


class Users(core.Base):

    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    email = Column(Unicode)
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)


# Contest (downvote) a sequence or collection, fork

collections = {
    "Language Learning": [],
    "Survival": [],
    "Greek Classics": [],
    "Children's Books": [],
    "Principles of Design": [],
    "Magazines & Periodicals": [],
    "Revolutionary Research": [],
    "Modern Non-fiction": [
        "gonetomorrow00bant", "scarecrow00mich",
        "roughjustice00jack", "runninghot00jayn"],
    "Textbooks": {
        "Security": ["crackingdessecre00elec"],
        "Mathematics": ["firstyearalgebra00well",
                        "fishsarithmeticn02fish"],
        "Psychology": [],
        "Science": {
            "Physics": [],
            "Biology": []
        }
    },
    "Historical": [],
    "Military Treatise & Tactics": ["artofwaroldestmi00suntuoft"],
    "Self Improvement": [],
    "Poetry": [],
    "American Classics": ["worksofcharlesdd04dick"],
    "Literary Compilations": ["masterpiecesofwo00gild"],
    "Poetry": ["worksofedgaralle01poee"],
    "Reference Books": ["ourwonderworldli07chic"],
    "Craftwork": ["ourwonderworldli07chic"],
    "Religious Texts": [],
    "Plays": []
}


def create_tables():
    Book.metadata.create_all(engine)


def add_content(cs=None, parent=None):
    cs = cs or collections    
    for key in cs:
        c = Collection(name=key)
        c.create()

        if parent:
            parent.subcollections.append(c)
            parent.save()

        if type(cs[key]) is dict:
            add_content(cs[key], parent=c)
        else:
            for book_id in cs[key]:
                try:
                    b = Book.get(archive_id=book_id)
                except:
                    b = Book(archive_id=book_id)
                    b.create()
                c.books.append(b)
                c.save()

def search_all(query, page=0, limit=0):
    if not query:
        return []        

    books = Book.search(query, field="name", limit=50, page=page)
    authors = Author.search(query, field="name", limit=5, page=page)
    collections = Collection.search(query, field="name", limit=20, page=page)
    sequences = Sequence.search(query, field="name", limit=20, page=page)
    author_names = AuthorName.search(query, field="name", limit=5, page=page)
    if author_names:
        for author_name in author_names:
            _author = author_name.author
            authors.append(_author)
            print(_author.books)
            books.extend(_author.books)
            print(books)             

    for author in authors:
        books.extend(author.books)

    _books = [b.dict() for b in books]

    fulltext_results = fulltext_search(query)['hits']['hits']
    for hit in fulltext_results:
        archive_id = hit['fields']['identifier'][0]

        for b in _books:
            if archive_id == b['archive_id']:
                b['matches'] = hit['highlight']['text']
        else:
            book = Book.get(archive_id=archive_id).dict()
            book['matches'] = hit['highlight']['text']
            books.append(book)

    return {
        'sequences': [s.dict() for s in sequences],
        'collections': [c.dict() for c in collections],
        'authors': [a.dict() for a in list(set(authors))],
        'books': _books
    }


def build():
    create_tables()
    add_content()
