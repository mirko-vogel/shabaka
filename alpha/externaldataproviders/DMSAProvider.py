#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''

from bs4 import SoupStrainer

from WebQuery import WebQuery
from ExternalDataProvider import ExternalDataProvider, ExternalArabicDataQuery

class DMSAQuery(WebQuery, ExternalArabicDataQuery):
    """ 
    Represent an asynchronous query to معجم اللغة العربية المعاصرة 
    via arabdict.com
    
    """
    def parse_webpage(self, bs):
        """ Parses the webpage passed as an BeautifulSoup object and returns a unicode """

        for div in bs.find_all("div", class_ = "dataRecord dict_1"):
            try:
                s = div.find("div", class_ = "termarAbicAr").text
                if not self._matches_query(s):  
                    continue

                definition_div = div.find("div", class_ = "termDefintion")
                # TODO: Investigate this hack ...
                lines = definition_div.text.replace("\n", "").split(u"•")
                t = u"\n".join(l.strip(u"،") for l in lines)
                
                # Eventually strip المزيد ...
                more_link = definition_div.find("a")                
                if more_link:
                    t = t[: -len(more_link.text)]
                return t
                
                                
            except: pass

        return ""

    def _get_soupstrainer(self):
        return SoupStrainer("div", class_ = "dataRecord dict_1")

    @property
    def result_as_html(self):
        """ Returns the result as html """
        result_lines = self.result.split("\n")
        if len(result_lines) == 1:
            return result_lines[0]
    
        meanings = "\n".join("<li>%s</li>" % l for l in result_lines[1:])
        return "%s<ul>%s</ul>" % (result_lines[0], meanings)
        
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

