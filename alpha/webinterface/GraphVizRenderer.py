#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''

import tempfile, os
import pygraphviz

from awg import ArabicWordGraph

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
        res = self.graph.search_arabic(q, 100, "*:5")
        result_nodes = list(res.index_results)
            
        # For each node:
        # - draw immediate neighbours with details
        # - second order neighbours without details
        # - always draw root path
        # - do not follow information edges
        # if not "much to display", draw verb derivations
        edges1, edges2 = set(), set()
        nodes1, nodes2 = set(), set()

        # If there are several results, draw search node
        if len(result_nodes) > 1:
            self.draw_search_node(q)
        
        for r in result_nodes:
            self.draw_result(r)
            if len(result_nodes) > 1:
                self.draw_search_edge(q, r)
            
            # Follow outgoing edges
            for e in r.outE:
                if e.cls == "InformationEdge":
                    continue
                nb = e.in_
                edges1.add(e)
                nodes1.add(nb)

                for e2 in nb.outE:
                    if e2.cls == "InformationEdge":
                        continue
                    nodes2.add(e2.in_)
                    edges2.add(e2)
                        
            # Follow incoming edges, indegree is always one.
            e = r.inE[0]    
            nb = e.out
            nodes1.add(nb)
            edges1.add(e)
            while len(nb.inE) > 0:
                edges2.add(nb.inE[0])
                nb = next(nb.in_)
                nodes2.add(nb)
        
        nodes2.difference_update(nodes1)
        edges2.difference_update(edges1)
        for n in nodes1:
            if n.cls == "Root":
                self.draw_root_node(n)
            else:
                self.draw_1st_nb(n)
        for n in nodes2:
            if n.cls == "Root":
                self.draw_root_node(n)
            else:
                self.draw_2nd_nb(n)
        for e in edges1:
            self.draw_1st_nb_edge(e)
        for e in edges2:
            self.draw_2nd_nb_edge(e)


    def draw_search_node(self, q):
        #html = '<font color="red">%s</font>' % q
        self.draw_node("SEARCH", q, shape = "oval", style = "filled", color = "darkslategrey", fontcolor="white", fontsize = 20)

    def draw_search_edge(self, q, n):
        self.draw_edge("SEARCH", n.rid, color = "darkslategrey")

    def draw_result(self, n):   
        url = "show?node_id=%s" % n.rid
        s = '<TABLE CELLBORDER="1" BORDER="0" CELLSPACING="0">'
        s += '<TR><TD BGCOLOR="BLACK"><FONT COLOR="WHITE" POINT-SIZE="20">%s</FONT></TD></TR>' % n.data["label"]
        translations = [e.in_.data["label"] for e in n.outE if e.cls == "InformationEdge" ]
        for t in translations:
            s += '<TR><TD>%s</TD></TR>' % t
        s += '</TABLE>'
                
        self.draw_node(n.rid, "<%s>" % s, URL = url,
                        shape = "plaintext")

    def draw_root_node(self, n):
        url = "show?node_id=%s" % n.rid
        html = '<FONT COLOR="GREY" POINT-SIZE="30">%s</FONT>' % n.data["label"]
        self.draw_node(n.rid, label = "<%s>" % html, URL = url,
                        shape = "plaintext")
    
    def draw_1st_nb(self, n):
        url = "show?node_id=%s" % n.rid
        s = '<TABLE CELLBORDER="1" BORDER="0" CELLSPACING="0">'
        s += '<TR><TD BGCOLOR="GREY"><FONT COLOR="WHITE" POINT-SIZE="16">%s</FONT></TD></TR>' % n.data["label"]
        t = next((e.in_.data["label"] for e in n.outE if e.cls == "InformationEdge"), None)
        if t:
            s += '<TR><TD>%s</TD></TR>' % t
        s += '</TABLE>'

        self.draw_node(n.rid, label = "<%s>" % s, URL = url, shape = "plaintext")

    def draw_2nd_nb(self, n):
        url = "show?node_id=%s" % n.rid
        s = '<TABLE CELLBORDER="1" BORDER="0" CELLSPACING="0">'
        s += '<TR><TD BGCOLOR="GREY"><FONT COLOR="WHITE" POINT-SIZE="16">%s</FONT></TD></TR>' % n.data["label"]
        s += '</TABLE>'

        self.draw_node(n.rid, label = "<%s>" % s, URL = url, shape = "plaintext")
    
    def draw_1st_nb_edge(self, e):
        self.draw_edge(e.out.rid, e.in_.rid)
    
    def draw_2nd_nb_edge(self, e):
        self.draw_edge(e.out.rid, e.in_.rid)
        
    def draw_node(self, name, label, **kwargs):
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
