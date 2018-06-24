#!/usr/bin/env python
#-*-coding: utf-8 -*-

"""
    __init__.py
    ~~~~~~~~~~~
    Configuration manager for Internet Archive API Server

    :copyright: (c) 2015 by Internet Archive
    :license: see LICENSE for more details.
"""

import os
import sys
import types
try:
    import configparser
except:
    import ConfigParser as configparser

path = os.path.dirname(os.path.realpath(__file__))
approot = os.path.abspath(os.path.join(path, os.pardir))

def getdef(self, section, option, default_value):
    try:
        return self.get(section, option)
    except:
        return default_value

config = configparser.ConfigParser()
config.read('%s/settings.cfg' % path)
config.getdef = types.MethodType(getdef, config)

HOST = config.getdef("server", "host", '0.0.0.0')
PORT = int(config.getdef("server", "port", 8080))
DEBUG = bool(int(config.getdef("server", "debug", 1)))
SECRET_KEY = config.getdef("sessions", "secret", "")
options = {'debug': DEBUG, 'host': HOST, 'port': PORT}

API_BASEURL = config.getdef("api", "url", "http://archive.org")
ES_URL = config.getdef("api", "es", "")

# Enable CORS to allow cross-domain loading of tilesets from this server
# Especially useful for SeaDragon viewers running locally
cors = bool(int(config.getdef('server', 'cors', 0)))

iiif_url = config.getdef('iiif', 'url', 'https://iiif.archivelab.org')
pragma_url = config.getdef('pragma', 'url', 'https://pragma.archivelab.org')

# DATABASES
DB_URI = '%(dbn)s://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s?client_encoding=utf8' % {
    'dbn': config.getdef('db', 'dbn', 'postgres'),
    'port': config.getdef('db', 'port', '5432'),
    'host': config.getdef('db', 'host', 'localhost'),
    'user': config.getdef('db', 'user', 'librarian'),
    'db': config.getdef('db', 'db', 'lists'),
    'pw': config.getdef('db', 'pw', '')
}

API_SERVER = "https://archive.org"
