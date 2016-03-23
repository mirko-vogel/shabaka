#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''

import pyorient
from pyarabic import araby
from ResultSet import ResultSet
from WrappedRecord import WrappedNode, WrappedEdge
import Tools


SQL_GET_NODE = """
select from %s 
"""

SQL_SEARCH = """
SELECT EXPAND(rid) FROM index:%s where key = '%s'
"""

SQL_SEARCH_BY_TRANSLATION = """
SELECT expand(rid.in()) from index:Node.label where key = '%s'
"""

# A node's subgraph is the subgraph induced by all words derived from the same
# root in addition to their translation.

# HACK: There must be a decent way to get these subgraphs
SQL_GET_NODE_FETCH_SUBGRAPH = """
select expand(bothE()) from (
    traverse both(), bothE() FROM [ %s ]
    while @class <> 'ForeignNode' )
"""

SQL_SEARCH_FETCH_SUBGRAPHS = """
select expand(bothE()) from (
    traverse both(), bothE() from (
        SELECT EXPAND(rid) FROM index:%s where key = '%s' )
    while @class <> 'ForeignNode' ) 
"""



class ArabicWordGraph(object):
    """
    
    """
    DEFAULT_FETCHPLAN = "*:1"
    DEFAULT_LIMIT = 1000
    
    def __init__(self, db_name = "shabaka", db_user = "admin", db_pwd = "admin"):
        """
        Establishes connection to OrientDB
        
        """
        self.client = pyorient.OrientDB()
        r = self.client.db_open(db_name, db_user, db_pwd, pyorient.DB_TYPE_GRAPH)
        self.cluster_ids = dict((c.name, c.id) for c in r)

    def search_index(self, q, fetch_subgraph = True, index = "Node.label", 
                     limit = DEFAULT_LIMIT, fetchplan = DEFAULT_FETCHPLAN,
                     primary_pred = None):
        """
        Runs a query against the given index, returning a ResultSet. If no
        predicate to differentiate between primary and secondary results is
        passed, index hits are considered primary results.
        
        """
        if fetch_subgraph:
            query = SQL_SEARCH_FETCH_SUBGRAPHS % (index, q)
        else:
            query = SQL_SEARCH % (index, q)

        if not primary_pred:
            primary_pred = lambda x: x.data.get(index.split(".")[-1]) == q

        rs = ResultSet.from_query(self.client, query, limit, fetchplan, primary_pred)
        return rs

    def get_nodes(self, rids, fetch_subgraph = True, limit = DEFAULT_LIMIT,
                 fetchplan = DEFAULT_FETCHPLAN):
        """
        Returns a ResultSet consisting of nodes with given rids and their
        subgraphs, unless you disable subgraph fetching.
        
        The nodes retrieved for the given rids are considered primary results.
        
        You will get an empty resultset:
        - when retrieving a ForeignNode together with its subgraph
          (because "a node's subgraph" is only defined for ArabicNodes)
        - when the rids is unknown
        - when rids is empty
         
        """
        if not rids:
            return ResultSet([])
        
        if fetch_subgraph:
            query = SQL_GET_NODE_FETCH_SUBGRAPH % ", ".join(rids)
        else:
            query = SQL_GET_NODE % ",".join(rids)
        rs = ResultSet.from_query(self.client, query, limit, fetchplan,
                                  lambda x: x.rid in rids)
        return rs


    def search_arabic(self, q, fetch_subgraph = True, limit = DEFAULT_LIMIT,
                      fetchplan = DEFAULT_FETCHPLAN):
        """
        Searches for given label intelligently handling vocalization.
        (This does not make much sense without a fetchplan as you will get
        index nodes only.)
        
        """
        # If query is not vocalized, search unvocalized index and eventually
        # return subtree
        if not araby.is_vocalized(q):
            return self.search_index(q, fetch_subgraph,
                                     "ArabicNode.unvocalized_label", limit,
                                     fetchplan)
            
        # If it is vocalized, search unvocalized index and check for
        # "compatibility" of vocalization
        matches = self.search_index(araby.strip_tashkeel(q), False,
                                    "ArabicNode.unvocalized_label", limit)
        rids = [n.rid for n in matches.primary_results
                if Tools.is_vocalized_like(q, n.data["label"])]
        # Ignore vocalization if there is no compatible one
        if not rids:
            rids = [n.rid for n in matches.primary_results]
        return self.get_nodes(rids, fetch_subgraph, limit, fetchplan)

    def search_foreign(self, q, limit = DEFAULT_LIMIT,
                      fetchplan = "*:0"):
        """
        Returns a ResultSet consisting of nodes connected to ForeignNodes
        whose label matches the query.
        
        """
        sql = SQL_SEARCH_BY_TRANSLATION % q
        return ResultSet.from_query(self.client, sql, limit, fetchplan) 

    
    def create_node(self, _class, label, **kwargs):
        """
        Creates node, handles conversion of unicode strings.
        Returns a WrappedNode.
        
        """
        # HACK: Why do we need to do this escaping?
        kwargs["label"] = label.translate({ord("\\"): u"\\\\"})
        r = self.client.record_create(self.cluster_ids[_class],
                                      Tools.encode_map(kwargs))
        return WrappedNode(r)

    def create_edge(self, _class, src, tgt, **kwargs):
        """
        Creates edge of given class (string) between src and tgt either passed as
        WrappedNodes or as RID strings. Returns a WrappedEdge.
        """
        if type(src) == WrappedNode:
            src = src.rid
        if type(tgt) == WrappedNode:
            tgt = tgt.rid
        r = self.client.command("CREATE EDGE %s from %s to %s CONTENT %s" % 
                                (_class, src, tgt, Tools.encode_map(kwargs)))
        return WrappedEdge(r[0])
    
    def create_arabic_node(self, cluster_name, label, **kwargs):
        """
        Checks that label is an arabic string, removes tatweel and normalizes 
        ligatures. Adds unvocalized_label.
        
        """
        label = araby.normalize_ligature(araby.strip_tatweel(label))
        label = label.replace(araby.SMALL_ALEF, "")
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
        edge_properties["stem"] = stem
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

    G = ArabicWordGraph()
    r = G.add_root_node(u"ه ل ك")
    n1 = G.add_foreign_node(u"\\u\\", "en", r)
    # n2 = graph.add_noun_node(u"اِسْتِهْلَاْكٌ", n1, edge_properties = {"type": "masdar"})
    # n3 = graph.add_noun_node(u"مُسْتَهْلِكٌ", n1, edge_properties = {"type": "pp"})
    for r in (G.get_nodes(["#15:39797"], fetchplan = "*:1"), G.search_arabic(u"فضل"), G.search_arabic(u"فضّل")):
        print len(r)
                
    for r in (G.get_nodes(["#13:45824"], False), G.search_arabic(u"فضل"), G.search_arabic(u"فضّل", False)):        
        for n in r.primary_results:
            print n.cls, n.rid, n.data["label"]
        print
        for n in r.secondary_results:
            print n.cls, n.rid, n.data["label"]
        print
