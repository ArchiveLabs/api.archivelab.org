#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    api/core.py
    ~~~~~~~~~~~

    Scholar API core

    :copyright: (c) 2015 by mek.
    :license: see LICENSE for more details.
"""


from . import db
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import ClauseElement

try:
    from http.client import HTTPException
except ImportError:
    from httplib import HTTPException


class ApiException(Exception):
    def __init__(self, msg, cause='', http_error_code=None, *args, **kwargs):
        Exception.__init__(self, msg, *args)

        self.msg = msg
        self.cause = cause
        self.http_error_code = http_error_code

        for k, v in kwargs.items():
            setattr(self, k, v)


class BaseMixin(object):

    query = db.query_property()

    __tablename__ = ''
    TBL = __tablename__
    PKEY = 'id'

    @classmethod
    def all(cls):
        return cls.query.all()

    @classmethod
    def get(cls, *args, **kwargs):
        """Generic 'smart' get function. Does different things based
        on number of arguments.  Some would call this a 'not smart'
        idea but we are not asking them.

        Single positional argument and no kwargs:
          args[0] is not of type ClauseElement:
            Looks up model by primary key of model specified by cls.PKEY
          args[0] is of type ClauseElement:
            Adds the clause emelemt to a where clause for a query on cls.

        Anything Else (any combination of multiple args and any kwargs):
          Converts all kwargs to clause elements, adds the args (all
          should be clause elements), and passes them together in as
          the where filter (all combined with AND) to a query on cls.
        """
        if len(args) == 1 and not isinstance(args[0], ClauseElement):
            terms = [getattr(cls, cls.PKEY) == args[0]]
        else:
            terms = list(args) + \
                [getattr(cls, k) == v for k, v in kwargs.items()]

        obj = cls.query.filter(*terms).first()
        if obj:
            return obj

        cause = dict(kwargs) if kwargs else list(args)
        raise ApiException(
            "Failed to get %s: %s" % (cls.__name__, cause),
            cause=list(cause.keys()) if kwargs else cause)

    def dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def remove(self, commit=True):
        """Potentially check if DBsession is "clean" and then commit
        only if it is, or if commit flag specified
        """
        db.delete(self)
        if commit:
            db.commit()

    def create_pre_hook(self):
        """Custom create logic to be overridden by inheriting classes"""
        pass

    def create_post_hook(self):
        """Custom create logic to be overridden by inheriting classes"""
        pass

    def create(self):
        """creates a new entry in cls.TBL with given data. Calls
        create_hook which is implemented/overridden by extending
        classes to handling custom validation"""
        self.create_pre_hook()
        return self._save()
        self.create_post_hook()

    def to_sql(q):
        return q.statement.compile(dialect=postgresql.dialect())

    def save_hook(self):
        """Custom create logic to be overridden by inheriting classes"""
        pass

    def save(self):
        """Save/update an existing entity. Saving should fail if the
        primary_key has no value set (requires create API to enforce
        validation rules for creation)
        """
        pid = getattr(self, self.PKEY, '')
        if not pid:
            raise ApiException(
                "Save operation requires primary key to be unset, "
                "i.e. record must alreay exist")
        self.save_hook()
        self._save(update=True)

    def _save(self, update=False):
        """Mechanism for raw, unchecked atomic saves"""
        if update:
            pid = getattr(self, self.PKEY)  # TODO: make sure pid setattr
            if not self.exists(**{self.PKEY: pid}):
                raise ApiException(
                    "Unable to save/update to %s entity with %s: %s. "
                    "Entry must first be created."
                    % (self.TBL, self.PKEY, pid))
        db.add(self)
        try:
            db.commit()
            return getattr(self, self.PKEY)
        except Exception as e:
            db.rollback()
            raise e

    @classmethod
    def get_several(cls, ids, lazy=False):
        q = db.query(cls).filter(cls.id.in_(ids))
        return q if lazy else q.all()

    @classmethod
    def exists(cls, *args, **kwargs):
        terms = None
        if len(args) == 1:
            if not isinstance(args[0], ClauseElement):
                terms = [getattr(cls, cls.PKEY) == args[0]]

        if not terms:
            terms = list(args) + \
                [getattr(cls, k) == v for k, v in kwargs.items()]

        res = db.query(getattr(cls, cls.PKEY)).filter(*terms).limit(1).first()
        if res:
            return res.id
        return False

    @classmethod
    def search(cls, query, field, limit=10, page=0):
        return cls.query.filter(getattr(cls, field).ilike("%" + query + "%"))\
            .offset(page * limit).limit(limit).all()


Base = declarative_base(cls=BaseMixin)
