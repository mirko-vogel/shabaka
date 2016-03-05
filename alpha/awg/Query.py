#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''

class Query(object):
    """
    """
    
    def __init__(self, query_string, options, awg):
        """
        Initializes a Query object with a unicode query string, a dictionary of
        options an an ArabicWordGraph object against which the query is to be
        run.
        
        """
        self.query_string = query_string
        self.options = options
        self.awg = awg
        self._results = None
        
    def run(self):
        """
        Runs the query if it has not already been run.
        
        """
        self._results = []
        
        # TODO: Add results
    
    @property
    def results(self):
        """
        Returns the result of the query as a list of node - description pairs,
        where node is a subclass of Node and the description is a (unicode)
        string. If nothing has been found, the list is empty.
        
        Runs the query if it has not already been run. 
        """
        if self._results == None:
            self.run()
            
        return self._results


class NoQuery(Query):
    """ Wraps a single node as if it was the result of a query  """
    
    def __init__(self, result_node, result_description = ""):
        self._results = [(result_node, result_description)]
    
    def run(self):
        pass

if __name__ == '__main__':
    pass