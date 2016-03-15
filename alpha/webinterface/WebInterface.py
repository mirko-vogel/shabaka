#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''

import cherrypy
from Cheetah.Template import Template
from awg import ArabicWordGraph
from webinterface import GraphVizRenderer

class GraphvizWebinterface(object):
    """
    
    """
    def __init__(self, graph = None):
        if not graph:
            graph = ArabicWordGraph()
        self.graph = graph
    
    def search(self, q):
        pass
    
    @cherrypy.exposed
    def show(self, rid):
        self.graph.get_node(rid, fetchplan = "*:3")
        renderer = GraphVizRenderer()
        
        vars = { "entry": center_node.entry, "svg": "\n".join(svg_lines[6:]) }
        
        tmpl = file("templates/show_entry.tmpl").read().decode("utf-8")
        t = Template(tmpl, searchList = [vars])
        return unicode(t).encode("utf8")

        