#!/usr/bin/env python
# encoding: utf-8
'''
Bla bal

@author:     Mirko Vogel
'''
import sys, os
import langenscheid_lookup

import cherrypy, cherrypy.lib.static
import tempfile
from Cheetah.Template import Template

from ArabicDictionary import ArabicDictionary
from ArabicDictionaryGraph import ArabicDictionaryGraph


class ArabicDictionaryServer(object):
    def __init__(self, adg):
        self.adg = adg
        
    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("show?node_id=2")

    @cherrypy.expose
    def search(self, citation_form):
        nodes = self.adg.search(citation_form)
        if nodes:
            return self._show(nodes[0])
        
        return "Sorry, nothing found."

    @cherrypy.expose
    def show(self, node_id):
        """Returns html page with embeded svg"""

        center_node = self.adg.nodes[int(node_id)]
        return self._show(center_node)

    def _show(self, center_node):
        G = self.adg.draw(center_node, 2)
        
        path = tempfile.mktemp(suffix = ".svg")
        G.draw(path, format = "svg", prog = "neato")
        svg_lines = open(path).readlines()
        os.unlink(path)
        
        try:
            li = langenscheid_lookup.lookup(center_node.entry.citation_form)
        except:
            li = []
            
        vars = { "entry": center_node.entry, "langenscheidt_info": li,
                 "svg": "\n".join(svg_lines[6:]) }
        
        tmpl = file("templates/show_entry.tmpl").read().decode("utf-8")
        t = Template(tmpl, searchList = [vars])
        return unicode(t).encode("utf8")

    
if __name__ == '__main__':
    l = ArabicDictionary()
    l.import_dump(sys.argv[1])
    adg = ArabicDictionaryGraph(l)
    server = ArabicDictionaryServer(adg)
    
    cherrypy.quickstart(server, '/', "cherrypy.conf")