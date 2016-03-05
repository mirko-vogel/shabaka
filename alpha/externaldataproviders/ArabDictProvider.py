#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''

from WebQuery import WebQuery
from ExternalDataProvider import ExternalDataProvider

import itertools
import urllib2

class ArabDictQuery(WebQuery):
    """ 
    
    """
    def parse_webpage(self, bs):
        """ Parses the webpage passed as an BeautifulSoup object and returns a unicode """
        translations = []

        for n in itertools.count(1):
            div = bs.find("div", id = "div_%s"  % n)
            if not div:
                break
            
            try:
                s = div.find("a", {"class": "arabic-term"}).text
                t = div.find("a", {"class": "latin-term"}).text
                # TODO: Check if s matches query string
                translations.append(t)
            except: pass
        
        return ", ".join(translations)
    
    @property
    def url(self):
        """ Returns the query url as unicode string, without url encoding """
        return "http://www.arabdict.com/de/deutsch-arabisch/%s" \
                % self.query_string.encode("utf-8")


class ArabDictProvider(ExternalDataProvider):
    """
    Thin wrapper around ExternalDataProvider to use ArabicDictQuery for queries.
    
    """
    QueryClass = ArabDictQuery

    @property
    def name(self):
        """ Returns the name of the provider """
        return "ArabDict" 

if __name__ == '__main__':
    s = u"سلطة"
    p = ArabDictProvider()
    q = p.query(s)
    r = q.result
    print r