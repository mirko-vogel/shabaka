#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''

import cherrypy
from Cheetah.Template import Template
from awg import ArabicWordGraph
from GraphvizRenderer import GraphvizRenderer
from externaldataproviders import AgglomerationProvider

class GraphvizWebinterface(object):
    """
    
    """
    def __init__(self, graph = None):
        if not graph:
            graph = ArabicWordGraph()
        self.graph = graph
        self.agglomeration_provider = AgglomerationProvider()

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("show?rid=14:7015")

    @cherrypy.expose
    def search(self, q):
        renderer = GraphvizRenderer()
        renderer.build_graph_for_query(q)
        
        vars = { "node": None,
                "svg": renderer.render_graph() }
        
        tmpl = file("web/templates/graphviz.tmpl").read().decode("utf-8")
        t = Template(tmpl, searchList = [vars])
        return unicode(t).encode("utf8")
    
    @cherrypy.expose
    def show(self, rid):
        renderer = GraphvizRenderer()
        renderer.build_graph_for_node("#" + rid)
        
        node = renderer.result_nodes[0]
        external_data = self.agglomeration_provider.query(node.data["label"])
        
        vars = { "node": node,
                "svg": renderer.render_graph(),
                "external_data": external_data }
        
        tmpl = file("web/templates/graphviz.tmpl").read().decode("utf-8")
        t = Template(tmpl, searchList = [vars])
        return unicode(t).encode("utf8")

if __name__ == '__main__':
    wi = GraphvizWebinterface()
    
    cherrypy.quickstart(wi, '/', "cherrypy.conf")
        