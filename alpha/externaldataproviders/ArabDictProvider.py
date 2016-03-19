#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''

from WebQuery import WebQuery
from ExternalDataProvider import ExternalDataProvider, ExternalArabicDataQuery

import sys, itertools
from pyarabic import araby

class ArabDictQueryBase(WebQuery, ExternalArabicDataQuery):
    """ 
    Represent an asynchronous query to arabdict.com
    
    """
    def parse_webpage(self, bs):
        """ Parses the webpage passed as an BeautifulSoup object and returns a unicode """
        translations = []

        for div in bs.find_all("div", id = self._div_id_matcher):
            try:
                s = div.find("a", {"class": "arabic-term"}).text
                t = div.find("a", {"class": "latin-term"}).text

                if self._matches_query(s):
                    translations.append(t)
                
            except: pass
        
        return ", ".join(translations)

    def _get_soupstrainer(self):
        """ See WebQuery._get_soupstrainer """
        return SoupStrainer("div", id = self._div_id_matcher)
    
    @staticmethod
    def _div_id_matcher(id):
        return id and id[0:4] == "div_" and id[4:].isdigit()
    

class GermanArabDictQuery(ArabDictQueryBase):
    @property
    def url(self):
        """ Returns the query url as unicode string """
        return "http://www.arabdict.com/de/deutsch-arabisch/%s" \
                % self.query_string


class EnglishArabDictQuery(ArabDictQueryBase):
    @property
    def url(self):
        """ Returns the query url as unicode string """
        return "http://www.arabdict.com/en/english-arabic/%s" \
                % self.query_string


class GermanArabDictProvider(ExternalDataProvider):
    """ Wrapper around ExternalDataProvider to use ArabicDictQuery for queries. """
    QueryClass = GermanArabDictQuery

    @property
    def name(self):  return "arabdict.de" 


class EnglishArabDictProvider(ExternalDataProvider):
    """ Wrapper around ExternalDataProvider to use ArabicDictQuery for queries. """
    QueryClass = EnglishArabDictQuery

    @property
    def name(self):  return "arabdict.com" 


if __name__ == '__main__':
    GermanArabDictProvider().run_cli()

