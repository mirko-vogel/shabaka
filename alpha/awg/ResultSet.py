#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''

from itertools import ifilter, ifilterfalse

from WrappedRecord import WrappedRecord

class ResultSet(object):
    @staticmethod
    def from_query(orientdb_client, query, limit = 1000, fetchplan = "*:0",
                   primary_pred = lambda x: True):
        """
        Creates a ResultSet by querying an OrientDB client.
        
        """
        results = []
        cb = lambda r: results.append(r)
        results += orientdb_client.query(query, limit, fetchplan, cb)
        return ResultSet(results, primary_pred)
    
    def __init__(self, results, primary_pred = lambda x: True):
        """
        Creates a ResultSet from OrientRecords, differentiating between primary
        and secondary results with the given predicate. This can be used, e.g.,
        when a query retrieves subtrees for search results.
        
        For each OrientRecord, either a WrappedEdge or a WrappedNode object is
        created. Then links are updated, see WrappedEdge.update_endpoints().
         
        """
        self.primary_pred = primary_pred
        self.result_map = {}
        self.index_results_rids = set()
        for r in results:
            try:
                wr = WrappedRecord.from_record(r)
                self.result_map[r._OrientRecord__rid] = wr
            except:
                print "Error parsing record %r" % r

        for r in self.result_map.itervalues():
            r.update_links(self.result_map)
    
    @property
    def first_result(self):
        """
        Returns the first primary result. If there are none, 
        returns the first result. Returns None if there are no results.
        
        Note that the order of search results is arbitrary, so use this
        function if you know that there is a single result or if you are happy
        with a random one.
        
        """
        r = next(self.primary_results, None)
        if not r:
            r = next(self.all_results, None)
        return r

    @property
    def has_single_primary_result(self):
        """ Returns whether there is a single primary result """
        # Ugly, something like next(next(x), []), None)
        return len(list(self.primary_results)) == 1

    @property
    def primary_results(self):
        """
        Returns an iterator over the primary results, where "primary" is defined
        by the predicate passed to __init__. 
        
        """
        return ifilter(self.primary_pred, self.all_results)

    @property
    def secondary_results(self):
        """ Returns an iterator over the secondary results. """
        return ifilterfalse(self.primary_pred, self.all_results)
    
    @property
    def all_results(self):
        """ Returns an iterator over all results """
        return self.result_map.itervalues()
    
    @property
    def edges(self):
        """ Returns an iterator over all results """
        return ifilter(lambda r: r.is_edge, self.result_map.itervalues())

    @property
    def nodes(self):
        """ Returns an iterator over all results """
        return ifilter(lambda r: not r.is_edge, self.result_map.itervalues())

    def __len__(self):
        return len(self.result_map)
    
    def _dump_stats(self):
        print "%d nodes / %d edges" % (len(list(self.nodes)), len(list(self.edges)))
        print "Node classes: "
        node_cls = set(n.cls for n in self.nodes)
        for c in sorted(node_cls):
            print "\t", c, len(list(n for n in self.nodes if n.cls == c))
        print "Edge classes: "
        edge_cls = set(e.cls for e in self.edges)
        for c in sorted(edge_cls):
            print "\t", c, len(list(e for e in self.edges if e.cls == c))

if __name__ == '__main__':
    import pyorient
    client = pyorient.OrientDB()
    client.db_open("shabaka", "admin", "admin", pyorient.DB_TYPE_GRAPH)
    
    q = "select expand(out()) from (TRAVERSE both(), bothE() FROM #15:39797 WHILE @class <> 'ForeignNode')"
    rs1 = ResultSet.from_query(client, q, fetchplan = "*:1")
    rs2 = ResultSet.from_query(client, q, fetchplan = "*:2")
    q = "select expand(outE()) from (TRAVERSE both(), bothE() FROM #15:39797 WHILE @class <> 'ForeignNode')"
    rs3 = ResultSet.from_query(client, q, fetchplan = "*:0")
    rs4 = ResultSet.from_query(client, q, fetchplan = "*:1")
    for rs in (rs1, rs2, rs3, rs4):
        rs._dump_stats()
    

    q = "select *, expand(out()) from (TRAVERSE both(), bothE() FROM #16:8342 WHILE @class <> 'ForeignNode')"
    rs = ResultSet.from_query(client, q, primary_pred = lambda x: x.rid == "#16:8342")
    for r in rs.primary_results:
        print r
    for r in rs.secondary_results:
        print r