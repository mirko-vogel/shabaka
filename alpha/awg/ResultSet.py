#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''

from itertools import ifilter, chain

from WrappedRecord import WrappedRecord

class ResultSet(object):
    @staticmethod
    def from_query(orientdb_client, query):
        """
        Creates a ResultSet by querying an OrientDB client.
        
        The records returned by callback are considered fetchplanr results.
        (This behaviour is not documented, though.)  
        
        """
        fetchplan_results = []
        cb = lambda r: fetchplan_results.append(r)
        # We cannot specify a callback without specifying fetchplan and limit
        # Use defaults - should be overwritten by what is given in query
        direct_results = orientdb_client.query(query, 20, "*:0", cb)
        return ResultSet(direct_results, fetchplan_results)
    
    def __init__(self, direct_results, fetchplan_results = [],
                 drop_index_results = False):
        """
        Creates a ResultSet from OrientRecords keeping track of the origin of
        the record.
        
        For each OrientRecord, either a WrappedEdge or a WrappedNode object is
        created. Then links are updated, see WrappedEdge.update_endpoints().
        
        If drop_index_results is given, consider the direct results as index
        nodes 
         
        """
        self.edges = []
        self.nodes = []
        result_map = dict((r._OrientRecord__rid, WrappedRecord.from_record(r))
                          for r in chain(direct_results, fetchplan_results))
        for r in result_map.itervalues():
            r.update_links(result_map)
            if r.is_edge:
                self.edges.append(r)
            else:
                self.nodes.append(r)
        
        self.direct_results_rids = [r._OrientRecord__rid for r in direct_results]

    @property
    def direct_results(self):
        return chain(self.direct_result_edges, self.direct_result_nodes)

    @property
    def direct_result_edges(self):
        return ifilter(lambda e: e.rid in self.direct_results_rids, self.edges)

    @property
    def direct_result_nodes(self):
        return ifilter(lambda e: e.rid in self.direct_results_rids, self.nodes)

    @property
    def fetchplan_results(self):
        return chain(self.fetchplan_result_edges, self.fetchplan_result_nodes)

    @property
    def fetchplan_result_edges(self):
        return ifilter(lambda e: e.rid not in self.direct_results_rids, self.edges)
    
    @property
    def fetchplan_result_nodes(self):
        return ifilter(lambda e: e.rid not in self.direct_results_rids, self.nodes)

    def _dump(self):
        print "Direct Results:"
        for r in chain(self.direct_result_edges, self.direct_result_nodes):
            print r
        print "Fetchplan Results:"
        for r in chain(self.fetchplan_result_edges, self.fetchplan_result_nodes):
            print r

if __name__ == '__main__':
    import pyorient
    client = pyorient.OrientDB()
    client.db_open("shabaka", "admin", "admin", pyorient.DB_TYPE_GRAPH)
    
    q1 = "SELECT FROM #22:8257"
    q2 = "SELECT FROM #22:8257 LIMIT 10 FETCHPLAN *:3"
    for q in (q1, q2):
        rs = ResultSet.from_query(client, q)
        rs._dump()