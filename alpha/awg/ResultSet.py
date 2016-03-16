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
        
        """
        results = []
        cb = lambda r: results.append(r)
        # We cannot specify a callback without specifying fetchplan and limit
        # Use defaults - should be overwritten by what is given in query
        results += orientdb_client.query(query, 20, "*:0", cb)
        return ResultSet(results)
    
    def __init__(self, results):
        """
        Creates a ResultSet from OrientRecords, deleting index records.
        
        For each OrientRecord, either a WrappedEdge or a WrappedNode object is
        created. Then links are updated, see WrappedEdge.update_endpoints().
         
        """
        self.result_map = {}
        self.index_results_rids = set()
        for r in results:
            wr = WrappedRecord.from_record(r)
            if wr.is_index_record:
                target_rid = "#" + wr.data["rid"]._OrientRecordLink__link
                self.index_results_rids.add(target_rid)
            else:
                self.result_map[r._OrientRecord__rid] = wr

        for r in self.result_map.itervalues():
            r.update_links(self.result_map)
    
    @property
    def index_results(self):
        """
        Returns the results that where found by looking up in an index.
        (Does not return the nodes representing index entries but the nodes
        or edges they point to.) 
        
        This is the "primary" search result when using an index lookup together
        with a fetchplan.
        
        """
        return (self.result_map[rid] for rid in self.index_results_rids)

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

if __name__ == '__main__':
    import pyorient
    client = pyorient.OrientDB()
    client.db_open("shabaka", "admin", "admin", pyorient.DB_TYPE_GRAPH)
    
    q1 = "SELECT FROM #22:8257"
    q2 = "SELECT FROM #22:8257 LIMIT 10 FETCHPLAN *:3"
    for q in (q1, q2):
        rs = ResultSet.from_query(client, q)
        for r in rs.all_results:
            print r