#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''

import pyorient
from pyarabic import araby
from ResultSet import ResultSet
from WrappedRecord import WrappedNode
import Tools

class ArabicWordGraph(object):
    """
    
    """
    def __init__(self, db_name = "shabaka", db_user = "admin", db_pwd = "admin"):
        """
        Establishes connection to OrientDB
        
        """
        self.client = pyorient.OrientDB()
        r = self.client.db_open(db_name, db_user, db_pwd, pyorient.DB_TYPE_GRAPH)
        self.cluster_ids = dict((c.name, c.id) for c in r)

    def search_index(self, q, index = "Node.label", limit = 100, fetchplan = "*:1"):
        """
        Runs a query against the label index, returns a ResultSet. 
        
        """
        query = "SELECT FROM index:%s where key = '%s' " \
                "LIMIT %s FETCHPLAN %s" % (index, q, limit, fetchplan)
        rs = ResultSet.from_query(self.client, query)
        return rs

    def search_arabic(self, q, limit = 100, fetchplan = "*:1"):
        """
        Searches for given label intelligently handling vocalization.
        """
        res = None
        # if word is vocalized, look for an exact match
        if araby.is_vocalized(q):
            res = self.search_index(q, limit = limit, fetchplan = fetchplan)
            
        # search ignoring vocalization
        if not res:
            res = self.search_index(araby.strip_tashkeel(q),
                        "ArabicNode.unvocalized_label", limit, fetchplan)

        return res

    
    def create_node(self, _class, label, **kwargs):
        """
        Creates node, handles conversion of unicode strings
        
        """
        try:
            kwargs["label"] = label
            return self.client.record_create(self.cluster_ids[_class],
                                         Tools.encode_map(kwargs))
        except:
            raise

    def create_edge(self, _class, src, tgt, **kwargs):
        """
        Creates edge of given class (string) between src and tgt either passed as
        WrappedNodes or as RID strings.
        """
        if type(src) == WrappedNode:
            src = src.rid
        if type(tgt) == WrappedNode:
            tgt = tgt.rid
        return self.client.command("CREATE EDGE %s from %s to %s CONTENT %s" % 
                                   (_class, src, tgt, Tools.encode_map(kwargs)))
    
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
    r = graph.search_arabic(u"أ ل ف",
                                 100, "*:2")
    #r._dump()
    r = graph.search_arabic(u"ألف", 10, "*:3")
    for n in r.index_results:
        print n.cls, n.rid, n.data["label"]
    print
    for n in r.nodes:
        print n.cls, n.rid, n.data["label"]
