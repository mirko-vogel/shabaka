#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''

import tempfile, os
import pygraphviz

from awg import ArabicWordGraph
import pyorient.ogm as ogm

def r2id(n):
    return n._id[1:].replace(":", "_")

class GraphvizRenderer(object):
    """
    
    """
    def __init__(self, graph = None):
        if not graph:
            graph = ArabicWordGraph()
        self.graph = graph
        self.G = pygraphviz.AGraph(directed = True, overlap = "scale")
        self.drawn = []

    def build_graph_for_arabic_query(self, q):
        res = self.graph.search_arabic_node(q, 100, "*:1")
            
        # For each node:
        # - draw immediate neighbours with details
        # - second order neighbours without details
        # - always draw root path
        # - do not follow information edges
        # if not "much to display", draw verb derivations
        edges1, edges2 = set(), set()
        nodes1, nodes2 = set(), set()

        # If there are several results, draw search node
        if len(res) > 1:
            self.draw_search_node(q)
        
        for r in res:
            self.draw_result(r)
            if len(res) > 1:
                self.draw_search_edge(q, r)
            
            # Follow outgoing edges
            for e in r.outE():
                if e.registry_name == "InformationEdge":
                    continue
                nb = e.outV()
                edges1.add(e)
                nodes1.add(nb)

                for e2 in nb.outE():
                    if e2.registry_name == "InformationEdge":
                        continue
                    nodes2.add(e2.outV())
                    edges2.add(e)
                        
            # Follow incoming edges, indegree is always one.
            e = r.inE()[0]    
            nb = e.inV()
            nodes1.add(nb)
            edges1.add(e)
            while len(nb.inE()) > 0:
                edges2.add(nb.inE()[0])
                nb = nb.in_()[0]
                nodes2.add(nb)
        
        nodes2.difference_update(nodes1)
        edges2.difference_update(edges1)
        for n in nodes1:
            self.draw_1st_nb(n)
        for n in nodes2:
            self.draw_2nd_nb(n)
        for e in edges1:
            self.draw_1st_nb_edge(e)
        for e in edges2:
            self.draw_2nd_nb_edge(e)


    def draw_search_node(self, q):
        self.draw_node(q, label = "SEARCH", shape = "plaintext")

    def draw_search_edge(self, q, n):
        self.draw_edge(q, r2id(n))

    def draw_result(self, n):
        url = "show?node_id=%s" % r2id(n)
        self.draw_node(r2id(n), label = "RESULT", URL = url,
                        shape = "plaintext")

    def draw_root_node(self, n):
        url = "show?node_id=%s" % r2id(n)
        self.draw_node(r2id(n), label = "ROOT", URL = url,
                        shape = "plaintext")
    
    def draw_1st_nb(self, n):
        url = "show?node_id=%s" % r2id(n)
        self.draw_node(r2id(n), label = "%s (1)" % n.label, URL = url,
                       shape = "plaintext")

    def draw_2nd_nb(self, n):
        url = "show?node_id=%s" % r2id(n)
        self.draw_node(r2id(n), label = "%s (2)" % n.label, URL = url,
                        shape = "plaintext")
    
    def draw_1st_nb_edge(self, e):
        self.draw_edge(r2id(e.outV()), r2id(e.inV()))
    
    def draw_2nd_nb_edge(self, e):
        self.draw_edge(r2id(e.outV()), r2id(e.inV()))
        
    def draw_node(self, name, label, **kwargs):
        if type(label) != unicode:
            label = label.decode("utf-8")
        print "N: %s (%s)" % (name, label)
        self.G.add_node(name, label = label, **kwargs) 

    def draw_edge(self, src, tgt, **kwargs):
        print "E: %s -> %s" % (src, tgt)
        self.G.add_edge(src, tgt, **kwargs)    

    def render_graph(self, format = "svg"):
        path = tempfile.mktemp(suffix = ".svg")
        self.render_graph_to_disk(path, format)
        file_content = open(path).readlines()
        os.unlink(path)
        return file_content

    def render_graph_to_disk(self, path, format = "svg"):
        """ Layouts graph and writes is in given format to path """
        self.G.draw(path, format = format, prog = "neato")
 
if __name__ == '__main__':
    q = u"ألف"
    renderer = GraphvizRenderer()
    renderer.build_graph_for_arabic_query(q)
    print renderer.G
    renderer.render_graph_to_disk("test.svg")       
