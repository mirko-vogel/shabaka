#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''

import cherrypy
from Cheetah.Template import Template
from WebInterface import WebInterface
from pyarabic import araby

class TextWebInterface(WebInterface):
    """
    
    """
    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("show?rid=14:7015")

    @cherrypy.expose
    def search(self, q):
        if not q:
            return self.instantiate_template([], q)
        
        if araby.is_arabicstring(q):
            res = self.graph.search_arabic(q, True)
            #res._dump_stats()
        else:
            res = self.graph.search_foreign(q)
            #res._dump_stats()
            res = self.graph.get_nodes([n.rid for n in res.nodes], True)

        if res.has_single_primary_result:
            return self.render_single_node_result(res.first_result)
        return self.instantiate_template(res.primary_results, q)
    
    @cherrypy.expose
    def show(self, rid):
        rid = "#" + rid
        res = self.graph.get_nodes([rid], True)
        # res._dump_stats()
        return self.render_single_node_result(res.first_result)

    def render_single_node_result(self, node):
        path = [node]
        while len(node.inE):
            node = next(node.in_)
            path.append(node)
        return self.instantiate_template(reversed(path), path[0].data["label"])
        
    def instantiate_template(self, nodes_to_render, query):
        vars = {"nodes_to_render": nodes_to_render, "query": query,
                "ap": self.agglomeration_provider}
        tmpl = file("web/templates/textview.tmpl").read().decode("utf-8")
        t = Template(tmpl, searchList = [vars])
        return unicode(t).encode("utf8")

if __name__ == '__main__':
    wi = TextWebInterface()
    
    cherrypy.quickstart(wi, '/', "cherrypy.conf")
        