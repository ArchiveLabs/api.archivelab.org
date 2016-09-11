#!/usr/bin/env python
#-*-coding: utf-8 -*-

"""
    scholar.py
    ~~~~~~~~~~
    To become scholar.archive.org

    :copyright: (c) 2015 by Internet Archive
    :license: see LICENSE for more details.
"""

import requests
from flask import Response, request, jsonify
from flask.views import MethodView
from views import rest_api, paginate
from api.archive import items, item, search, collections


class Networks(MethodView):
    @rest_api
    def get(self):
        return {'networks': ['ALALAM', 'TRTTURK', 'CNBC', 'VIETFACETV', 'BLOOMBGERM', 'GLVSN', 'SYRIANDRAMA', 'PALESTINETV', 'WZDC', 'CNNW', 'ALETEJAHTV', 'TELECONGO', 'ALFAYHAA', 'WDR', 'NDTV', 'KKPX', 'ETV', 'MSNBC', 'TRT1', 'COM', 'NEWTV', 'RT', 'KDTV', 'KTSF', 'FRANCE24', 'OMAN', 'TV7TUNIS', 'IRIB2', 'KBCW', 'NILE', 'RAI', 'KFSF', 'BBCARABIC', 'WPXW', 'JORDANTV', 'WBFF', 'RTSSAT', 'KQED', 'KTEH', 'ALJAZ', 'NEWSW', 'WHUT', 'KUWAIT', 'SUDAN', 'SCOLA', 'BBC', 'TSR1', 'COMW', 'JAMAHIRYA', 'KSTS', 'KPIX', '3ABN', 'KCSM', 'WETA', 'KMTP', 'IRAQ', 'WMDO', 'KICU', 'FOXNEWSW', 'IRINN', 'CCTV9', 'CSPAN-EAST', 'WJLA', 'CCTV4', 'SHARJAHTV', 'TGN', 'BBCNEWS', 'CCTV3', 'NTV', 'ESC1', 'FUTURE', 'WTTG', 'BELARUSTV', 'NTA', 'WSBK', 'PSC', 'KTLA', 'WUTB', 'TELESUR', 'ALMAGHRIBIA', 'TV5MONDE', 'LIBYA', 'TAPESH', 'WMPT', 'ALIRAQUIA', 'SKY', 'KURDSAT', 'SCOLA5', 'CSPAN2E', 'WMAR', 'SAUDI', 'KNTV', 'BBC1', 'DW', 'CSPAN', 'BBC2', 'AZT', 'BET', 'WRC', 'WFDC', 'MSNBCW', 'ALFORAT', 'ANT1', 'NHK', 'MBC', 'TCN', 'KRON', 'KTLN', 'WJZ', 'CANALALGERIE', 'KCSMMHZ', 'TVRI', 'WBAL', 'YEMENTV', 'SOUTHERNSUDAN', 'DUBAI', 'WGN', 'ORTM', 'CUBA', 'KRCB', 'M2MOROCCO', 'KTVU', 'CSPN2', 'MTV', 'WORLDNET', 'AZTV', 'SCOLA2', 'PRESSTV', 'QATARTV', 'SCOLA6', 'WNUV', 'SCOLA4', 'RTPI', 'CNN', 'TELEPADREPIO', 'RTSDIASPORA', 'SFGTV2', 'SYRIANTV', 'MCM', 'SAMAYEAZADI', 'SCOLA3', 'LINKTV', 'VTV4', 'WUSA', 'ZEETV', 'FOXNEWS', 'KBSWORLD', 'KCNS', 'HLN', 'KTNC', 'KOFY', 'SFGTV', 'KGO']}


class Shows(MethodView):
    @rest_api
    @paginate()
    def get(self, network, page=1, limit=100):
        return search('mediatype:"collection" AND subject:"%s"' % network,
                      page=page, limit=limit)

class Episodes(MethodView):
    @rest_api
    @paginate()
    def get(self, network, show, page=1, limit=100):
        q = item(iid=show)['metadata']['search_collection']
        try:
            return search(q, page=page, limit=limit)
        except Exception as e:
            raise ValueError("This show has no episodes.")


class Episode(MethodView):
    @rest_api
    def get(self, network, show, episode):
        return item(iid=episode)


urls = (
    '/<network>/<show>/<episode>', Episode,
    '/<network>/<show>', Episodes,
    '/<network>', Shows,
    '', Networks
)
