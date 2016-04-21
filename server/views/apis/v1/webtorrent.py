#!/usr/bin/env python
#-*-coding: utf-8 -*-

"""
    webtorrent.py
    ~~~~~~~~
    Support for webtorrents of IA items.
    :copyright: (c) 2016 by Internet Archive
    :license: see LICENSE for more details.
"""

from flask import Response
from flask.views import MethodView
from api import mimetype, download

class File(MethodView):
    def get(self, iid, filename):
        """Download the specified file
        """
        return Response(download(iid, filename),
                        mimetype=mimetype(filename))

class Torrent(MethodView):
    def get(self, iid):
        """ Return a torrent with the webseed set correctly for webtorrents
        """
        return Response()

urls = (
    '/files/<iid>/<filename>', File,
    '/torrent/<iid>', Torrent
  )
