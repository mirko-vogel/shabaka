#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
from lxml.html import soupparser
from lxml import etree
import sys

"""
>>> import pygraphviz as pgv
>>> G=pgv.AGraph()
>>> G.add_node(u'')
>>> G.add_edge(u'', 'test')
>>> G.layout()
>>> G.draw("simple.png")
"""


RESULT_BLOCK_CLASS = "result-block"

ENTRY_CLASS = "lkgEntry"
LEMMA_CLASS = "lkgLemma lkgBig"
EXT_LEMMA_CLASS = "lkgEx lkgBig"
TRANSCRIPTION_CLASS = "lkgPhon"
TRANSLATION_CLASS = "lkgNormal"
SENSE_GROUP_CLASS = "lkgSenseIGp"

def get_children_by_class(root, cls):
    if type(cls) not in (tuple, list):
        cls = [cls]
    return [e for e in root.iter() if e != root and e.get("class") in cls]

def get_child_by_class(root, cls):
    children = get_children_by_class(root, cls)
    if len(children) > 1:
        raise RuntimeError("Expected a single child element of class %s" % cls)
    return children[0]

def has_child_of_class(root, cls):
    if type(cls) not in (tuple, list):
        cls = [cls]
    for e in root.iter():
        if e.get("class") in cls:
            return True
    return False

def get_text(root):
    txt = [e.text for e in root.iter() if e.text]
    return " ".join(txt) 

def handle_result_block(e):
    # compound block
    if has_child_of_class(e, SENSE_GROUP_CLASS):
        return
        handle_entry(e)
        groups = get_children_by_class(e, SENSE_GROUP_CLASS)
        for g in groups:
            handle_entry(g)
    else:
        handle_entry(e)

def handle_entry(e):
    lemma = get_text(get_child_by_class(e, [LEMMA_CLASS, EXT_LEMMA_CLASS]))
    transcription = get_text(get_child_by_class(e, TRANSCRIPTION_CLASS))
    translations = [get_text(c) for c in get_children_by_class(e, TRANSLATION_CLASS)]
    print "%s %s: %s" % (lemma, transcription, ", ".join(translations))


url = "http://de.langenscheidt.com/arabisch-deutsch/%s" % sys.argv[1]
#print "Fetching %s" % url
doc = urllib.urlopen(url).read()
root = soupparser.fromstring(doc)
for e in get_children_by_class(root, RESULT_BLOCK_CLASS):
    handle_result_block(e)