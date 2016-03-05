#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''

from WebQuery import WebQuery
from ExternalDataProvider import ExternalDataProvider

import sys, itertools
from pyarabic import araby

class ArabDictQuery(WebQuery):
    """ 
    Represent an asynchronous query to arabdict.com
    
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

                # TODO: Improve results filtering, check for "compatible" tashkeel"
                if araby.strip_tashkeel(self.query_string) == araby.strip_tashkeel(s): 
                    translations.append(t)
                
            except: pass
        
        return ", ".join(translations)
    
    @property
    def url(self):
        """ Returns the query url as unicode string """
        return "http://www.arabdict.com/de/deutsch-arabisch/%s" \
                % self.query_string


class ArabDictProvider(ExternalDataProvider):
    """ Wrapper around ExternalDataProvider to use ArabicDictQuery for queries. """
    QueryClass = ArabDictQuery

    @property
    def name(self):  return "ArabDict" 

if __name__ == '__main__':
    ArabDictProvider().run_cli()

