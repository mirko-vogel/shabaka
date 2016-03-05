#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''
from threading import Thread
import sys

class ExternalDataQuery(Thread):
    """
    Represents an asynchronous query to an ExternalDataProvider
    
    """
    
    def __init__(self, query_string):
        Thread.__init__(self)
        self.query_string = query_string
        self._result = None
        
    def run(self):
        raise NotImplementedError

    @property
    def result(self):
        """
        Returns the result of the query, waits for the query to be finished.
        
        """
        self.join()
        return self._result
        

class ExternalDataProvider(object):
    """
    Represents an external data source that can be queried for additional
    information like a dictionary, wikipedia, etc.
    
    Caches the results. 
    
    """
    QueryClass = ExternalDataQuery
    
    def __init__(self):
        self.cache = {}
    
    def query(self, query_string):
        """
        Immediately returns an ExternalData object, that runs the query
        asynchronously. If this query has been run before, the cached result is
        returned.
        
        """
        if query_string not in self.cache:
            q = self.QueryClass(query_string)
            q.start()
            self.cache[query_string] = q
            
        return self.cache[query_string]
    
    @property
    def name(self):
        """ Returns the name of the provider """
        raise NotImplementedError

    def run_cli(self):
        """ Run command line interface, reading input line by line """
        while True:
            s = raw_input("> ").decode("utf-8")
            r = self.query(s).result
            sys.stdout.write(r.encode("utf-8") + "\n")

if __name__ == '__main__':
    pass