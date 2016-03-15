#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''

import pyorient.ogm as ogm
from pyarabic import araby
from pyorient.otypes import OrientRecord

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
    """  Recursively encodes unicode string in keys and values """
    return recursive_map(m, lambda x: x.decode("utf-8"), lambda x: type(x) == str)


class ArabicWordGraph(object):
    """
    
    """
    def __init__(self, db_name = "shabaka", db_user = "root", db_pwd = "triangle"):
        """
        Establishes connection to OrientDB
        
        """
        config = ogm.Config("localhost", 2424, db_user, db_pwd, db_name)
        self.OG = ogm.Graph(config)
        self.OG.include(self.OG.build_mapping(ogm.declarative.declarative_node(),
                                              ogm.declarative.declarative_relationship(),
                                              auto_plural = True))
        
        self.cluster_ids = self.OG.client._cluster_map

    def get_node(self, rid, limit = 100, fetchplan = "*:0"):
        res = []
        self.OG.client.query("SELECT FROM %s" % rid, limit, fetchplan, lambda x: res.append(x))

        return res

    def search_arabic_node(self, q, limit = 100, fetchplan = "*:1"):
        """
        Searches for a node with given label intelligently handling vocalization.
        """
        res = []
        # if word is vocalized, look for an exact match
        if araby.is_vocalized(q):
            query = "SELECT FROM index:Node.label where key = '%s'" % q
            self.OG.client.query(query, limit, fetchplan, lambda x: res.append(x))
            if res:
                return res
            
        # search ignoring vocalization
        query = "SELECT FROM index:ArabicNode.unvocalized_label WHERE key = '%s'" \
                    % araby.strip_tashkeel(q)
        self.OG.client.query(query, limit, fetchplan, lambda x: res.append(x))
        
        for r in res:
            r.oRecordData["label"] = r.oRecordData["label"].decode("utf-8")
        
        return self.OG.elements_from_records(res)

    
    def create_node(self, _class, label, **kwargs):
        """
        Creates node, handles conversion of unicode strings
        
        """
        try:
            kwargs["label"] = label
            return self.OG.client.record_create(self.cluster_ids[_class],
                                         encode_map(kwargs))
        except:
            raise

    def create_edge(self, _class, src, tgt, **kwargs):
        """
        Creates edge of given class (string) between src and tgt either passed as
        OrientDB objects or as RID strings.
        """
        if type(src) == OrientRecord:
            src = src._OrientRecord__rid
        if type(tgt) == OrientRecord:
            tgt = tgt._OrientRecord__rid
        return self.OG.client.command("CREATE EDGE %s from %s to %s CONTENT %s" % 
                                   (_class, src, tgt, encode_map(kwargs)))
    
    def create_arabic_node(self, cluster_name, label, **kwargs):
        """
        Checks that label is an arabic string, removes tatweel and normalizes 
        ligatures. Adds unvocalized_label.
        
        """
        label = araby.normalize_ligature(araby.strip_tatweel(label))
        if not araby.is_arabicstring(label):
            raise RuntimeError("'%s' is not an Arabic string" % label)
        
        if "unvocalized_label" not in kwargs:
            kwargs["unvocalized_label"] = araby.strip_tashkeel(label)
        
        return self.create_node(cluster_name, label, **kwargs)

    def create_derived_node(self, node_class, label, origin_node, edge_class,
                              node_properties = {}, edge_properties = {}):
        """
        Create node and connects it
        """
        n = self.create_arabic_node(node_class, label, **node_properties)
        e = self.create_edge(edge_class, origin_node, n, **edge_properties)
        return (n, e)


    ## ---------------------------------------------------------------------
    ## Adding nodes to the graph an connecting them
    
    def add_root_node(self, label, **kwargs):
        return self.create_arabic_node("root", label, **kwargs)

    def add_verb_node(self, label, stem, derived_from, node_properties = {}, edge_properties = {}):
        edge_properties[stem] = stem
        (n, e) = self.create_derived_node("verb", label, derived_from,
                              "verbderivationedge", node_properties, edge_properties)
        return n

    def add_noun_node(self, label, derived_from, node_properties = {}, edge_properties = {}):
        (n, e) = self.create_derived_node("noun", label, derived_from,
                              "nounderivationedge", node_properties, edge_properties)
        return n

    def add_particle_node(self, label, derived_from, node_properties = {}, edge_properties = {}):
        (n, e) = self.create_derived_node("particle", label, derived_from, 
                                          "edge", node_properties, edge_properties)
        return n

    def add_foreign_node(self, label, language, derived_from, node_properties = {}, edge_properties = {}):
        node_properties["language"] = language
        n = self.create_node("foreignnode", label, **node_properties)
        self.create_edge("informationedge", derived_from, n, **edge_properties)
        return n

        
        
if __name__ == '__main__':
    graph = ArabicWordGraph()
    # r = graph.add_root_node(u"ه ل ك")
    # n1 = graph.add_verb_node( u"اِسْتَهْلَكَ", "X", r)
    # n2 = graph.add_noun_node(u"اِسْتِهْلَاْكٌ", n1, edge_properties = {"type": "masdar"})
    # n3 = graph.add_noun_node(u"مُسْتَهْلِكٌ", n1, edge_properties = {"type": "pp"})
    #r = graph.search_arabic_node(u"َخَرَج")

    r = graph.search_arabic_node(u"َخَرَج", 100, "*:2")
    for e in r:
        print e
        try:
            print e.inE()
            #print e.in_()
        except:
            print e.inV()
            print e.outV()