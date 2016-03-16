#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''
from io import BytesIO
from struct import unpack

def recursive_map(m, f, pred):
    """
    Recursively encodes unicode string in keys and values of given map thus
    creating a new map and returns it.
    
    """
    n = {}
    for (k, v) in m.iteritems():
        if pred(k): k = f(k)
        if pred(v): v = f(v)
        elif type(v) == list:
            v = [f(x) for x in v if pred(x)]
        if type(v) == map:
            v = recursive_map(v)
        n[k] = v

    return n

def encode_map(m):
    """  Recursively encodes unicode string in keys and values """
    return recursive_map(m, lambda x: x.encode("utf-8"), lambda x: type(x) == unicode)

def decode_map(m):
    """  Recursively decodes utf-8 encoded string in keys and values """
    return recursive_map(m, lambda x: x.decode("utf-8"), lambda x: type(x) == str)

def rid_data_to_rids(data):
    stream = BytesIO(data)
    (a,l) = unpack("!bi", stream.read(5))
    return ["#%d:%d" % unpack("!hq", stream.read(10))]

