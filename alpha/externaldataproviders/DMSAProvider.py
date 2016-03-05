#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''

from WebQuery import WebQuery
from ExternalDataProvider import ExternalDataProvider
from pyarabic import araby

import sys

class DMSAQuery(WebQuery):
    """ 
    Represent an asynchronous query to معجم اللغة العربية المعاصرة 
    via arabdict.com
    
    """
    def parse_webpage(self, bs):
        """ Parses the webpage passed as an BeautifulSoup object and returns a unicode """

        for div in bs.findAll("div", {"class": "dataRecord dict_1"}):
            try:
                s = div.find("div", {"class": "termarAbicAr"}).text
                # TODO: Improve results filtering, check for "compatible" tashkeel"
                if s != self.query_string:  
                    continue

                definition_div = div.find("div", {"class": "termDefintion"})
                # TODO: Investigate this hack ...
                t = u"\n•".join(definition_div.text.split(u"•"))
                
                # Eventually strip المزيد ...
                more_link = definition_div.find("a")                
                if more_link:
                    t = t[: -len(more_link.text)]
                return t
                
                                
            except: pass

        return ""
        
    @property
    def url(self):
        """ Returns the query url as unicode string """
        return u"http://www.arabdict.com/de/عربي-عربي/%s" % self.query_string


class DMSAProvider(ExternalDataProvider):
    """ Wrapper around ExternalDataProvider to use ArabicDictQuery for queries. """
    QueryClass = DMSAQuery

    @property
    def name(self):  return u"معجم اللغة العربية المعاصرة" 

if __name__ == '__main__':
    DMSAProvider().run_cli()

