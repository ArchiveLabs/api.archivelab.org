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
        t = bencode.bdecode(''.join(list(download(iid, iid + '_archive.torrent'))))
        t['url-list'] = ['https://api.archive.org/v2/webtorrent/files/']
        return Response(bencode.bencode(t), mimetype=mimetype(iid + '_archive.torrent'))

urls = (
    '/files/<iid>/<filename>', File,
    '/torrent/<iid>', Torrent
  )
