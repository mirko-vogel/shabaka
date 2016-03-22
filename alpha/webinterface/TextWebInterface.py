#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''

import cherrypy
from Cheetah.Template import Template
from GraphvizRenderer import GraphvizRenderer
from WebInterface import WebInterface
from awg.ResultSet import ResultSet
from awg.Tools import stem_to_int
from _collections import defaultdict

SEARCH_SQL = """
SELECT FROM (
  TRAVERSE both() FROM (
    SELECT expand(rid) FROM
    index:ArabicNode.label
    WHERE key = '%s' )
  WHILE @class <> 'ForeignNode' )
LIMIT 500 FETCHPLAN *:4
"""

class TextWebInterface(WebInterface):
    """
    
    """
    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("show?rid=14:7015")

    @cherrypy.expose
    def search(self, q):
        q = SEARCH_SQL % q
        resultset = ResultSet.from_query(self.graph.client, q)
    
    @cherrypy.expose
    def show(self, rid):
        rid = "#" + rid
        q = "SELECT FROM (TRAVERSE both() FROM %s " \
              "WHILE @class <> 'ForeignNode') LIMIT 500 FETCHPLAN *:4" % rid
        resultset = ResultSet.from_query(self.graph.client, q)

        ap = self.agglomeration_provider
        node = resultset.result_map[rid]
        path = [node]
        while not node.cls == "Root":
            node = next(node.in_)
            path.append(node)
        
        node = resultset.result_map[rid]
        node_data = ap.query(node.data["label"])
        vars = {"noun_node": None, "verb_node": None,
                "query": node.data["label"],
                "nodes_to_render": path}

        # Displaying a noun
        if node.cls == "Noun":
            vars["noun_node"] = node
            vars["noun_data"] = node_data 

        # Walk back to root, pick up verb when passing by
        while node.cls != "Root":
            if node.cls == "Verb":
                vars["verb_node"] = node
                vars["verb_data"] = ap.query(node.data["label"])
                # Fetch other derivations from verb
                vars["verb_derived_nouns"] = \
                    list(node.traverse_children(lambda x: x.cls == "Noun"))
            node = next(node.in_)
                
        # Collect derived verbs, sort
        vars["root"] = node.data["label"]
        vars["stems"] = [(n.inE[0].data["stem"], n)
                         for n in node.out if n.cls == "Verb"]
        vars["stems"].sort(key=lambda (s, n): stem_to_int(s))
        
        # Collect derived nouns
        vars["root_derived_nouns"] = \
            list(node.traverse_children(lambda x: x.cls == "Noun"))

        tmpl = file("web/templates/textview.tmpl").read().decode("utf-8")
        # Parameters for template:
        # - root, stems
        # - verb_node, verb_data, derived_nodes
        # - noun_node, noun_data
        t = Template(tmpl, searchList = [vars])
        return unicode(t).encode("utf8")

if __name__ == '__main__':
    wi = TextWebInterface()
    
    cherrypy.quickstart(wi, '/', "cherrypy.conf")
        