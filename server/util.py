#!/usr/bin/env python
#-*-coding: utf-8 -*-

"""
    util.py
    ~~~~~~~
    General purpose utilities

    :copyright: (c) 2015 by Internet Archive
    :license: see LICENSE for more details.
"""

try:
    from urlparse import urlparse
except:
    from urllib import parse as urlparse

def domain(url):
    """Returns the domain of a url"""
    return '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(url))
