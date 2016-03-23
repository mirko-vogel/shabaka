#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''
from io import BytesIO
from struct import unpack
from pyarabic import araby

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

def is_vocalized_like(w1, w2, ignore_shaddas = False):
    """
    Returns if two arabic unicode strings have compatible vocalization.
    
    Per default, shaddas are considered as characters and must be matched. Set
    ignore_shaddas to True to consider them as harakat and this inore them. 
    
    Adapted from pyarabic.araby.vocalized_similarity

    >>> vocalized_like(u"ألف", u"ألّف")
    False
    >>> vocalized_like(u"ألف", u"ألّف", True)
    True
    
    """
    
    pop = lambda x: x.pop() if x else None
    w1, w2 = list(w1), list(w2)
    c1, c2 = pop(w1), pop(w2)

    vowels = list(araby.HARAKAT)
    if ignore_shaddas:
        vowels.append(araby.SHADDA)
        
    while c1 or c2:
        if c1 == c2:
            c1, c2 = pop(w1), pop(w2)
        elif c1 in vowels and c2 not in vowels:
            c1 = pop(w1)
        elif c1 not in vowels and c2 in vowels:
            c2 = pop(w2)
        else:
            return False
            
    return True 

def stem_to_int(s):
    return {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6,
        "VII": 7, "VIII": 8, "IX": 9, "X": 10}.get(s)
