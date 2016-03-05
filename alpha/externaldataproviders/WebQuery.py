#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''

import urllib2
from BeautifulSoup import BeautifulSoup
from ExternalDataProvider import ExternalDataQuery 

class WebQuery(ExternalDataQuery):
    """
    Represents an asynchronous query to a WebDataProvider

    """
    def run(self):
        """
        Retrieves the web page at self.url and parses the result by calling
        self.parse_webpage(). Finally sets self._result.
        
        """
        request = urllib2.Request(self.url.encode("utf-8"))
        request.add_header('User-Agent', 'ShabakaWebQuery/0.1 +http://shabaka.redredblue.de')
        doc = urllib2.build_opener().open(request).read()

        bs = BeautifulSoup(doc)
        self._result = self.parse_webpage(bs)

    def parse_webpage(self, bs):
        """ Parses the webpage passed as an BeautifulSoup object and returns a unicode """
        raise NotImplementedError
    
    @property
    def url(self):
        """ Returns the query url as unicode string, without url encoding """
        raise NotImplementedError


if __name__ == '__main__':
    pass