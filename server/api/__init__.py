#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    api/__init__.py
    ~~~~~~~~~~~~~~~
    Initialization & DB Connections for scholar
    :copyright: (c) 2015 by mek.
    :license: see LICENSE for more details.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from configs import DB_URI, DEBUG
from . import archive

engine = create_engine(DB_URI, echo=DEBUG)
db = scoped_session(sessionmaker(bind=engine))
