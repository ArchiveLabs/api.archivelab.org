#!/usr/bin/env python
#-*-coding: utf-8 -*-

"""
    webtorrent.py
    ~~~~~~~~~~~~~

    Support for webtorrents of IA items.

    :copyright: (c) 2016 by Internet Archive
    :license: see LICENSE for more details.
"""

import better_bencode
from flask import Response
from flask.views import MethodView
from api import mimetype, download
from .items import File, Files


class Torrent(MethodView):
    def get(self, iid):
        """ Return a torrent with the webseed set correctly for webtorrents
        """
        fs = download(iid, iid + '_archive.torrent').content
        t = better_bencode.loads(fs)
        print(t)
        t[b'url-list'] = [b'https://api.archivelab.org/v2/webtorrents/files/']
        t[b'announce'] = b'wss://tracker.webtorrent.io'
        t[b'announce-list'] = [[b'wss://tracker.webtorrent.io'], [b'wss://tracker.btorrent.xyz'], [b'wss://tracker.fastcast.nz'], [b'wss://tracker.openwebtorrent.com']]
        return Response(
            better_bencode.dumps(t),
            mimetype=mimetype(iid + '_archive.torrent')
        )


urls = (
    '/files/<iid>/<filename>', File,
    '/files/<iid>/', Files,
    '/torrents/<iid>', Torrent
  )
