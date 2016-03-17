#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''

import tempfile, os
import pygraphviz
from collections import defaultdict

from awg import ArabicWordGraph
from awg.WrappedRecord import FakeEdge, FakeNode


class GraphvizRenderer(object):
    """
    
    """
    def __init__(self, graph = None):
        if not graph:
            graph = ArabicWordGraph()
        self.graph = graph
        self.G = pygraphviz.AGraph(directed = True, overlap = "scale")
        self.object_drawer = GraphVizObjectDrawer(self.G)

    def build_graph_for_query(self, q):
        res = self.graph.search_arabic(q, 100, "*:5")
        result_nodes = list(res.index_results)
        if len(result_nodes) > 1:
            self._build_graph_for_several_results(q, result_nodes)
            
        self.object_drawer.draw_objects()
    
    def build_graph_for_node(self, rid):
        """ Builds a graph for a single node  """
        rs = self.graph.get_node(rid, 100, "*:5")
        r = rs.result_map.get(rid)
        if r:
            self._build_graph_for_single_result(r)
            self.object_drawer.draw_objects()

    def _build_graph_for_several_results(self, q, result_nodes):
        """
        Draws search node and connects it to result nodes draw with
        _build_graph_for_single_result.
        
        """
        # Create fake node for query and connect it with fake edges to results
        n = FakeNode(rid = "SEARCH", data = {"label": q})
        self.object_drawer.add_object(n, "n_search")
        
        for r in result_nodes:
            e = FakeEdge(FakeNode(rid = "SEARCH"), r)
            self.object_drawer.add_object(e, "e_search")
            
            self._build_graph_for_single_result(r)

    def _build_graph_for_single_result(self, r):
        """
        Draws a result node with "attched graph":
        - draw immediate neighbours with details
        - second order neighbours without details
        - always draw root path
        - do not follow information edges
        
         TODO: if not "much to display", draw verb derivations
         
         """
        self.object_drawer.add_object(r, "n_result")
        # Add result children and children's children (+ edges)
        for child_edge in r.outE:
            if child_edge.cls == "InformationEdge":
                continue
            child = child_edge.in_
            self.object_drawer.add_object(child_edge, "e1")
            self.object_drawer.add_object(child, "n1")

            for child_edge_2 in child.outE:
                if child_edge_2.cls == "InformationEdge":
                    continue
                self.object_drawer.add_object(child_edge_2.in_, "n2")
                self.object_drawer.add_object(child_edge_2, "e2")
                    
        # Walk up if not already at root
        if r.cls == "Root":
            return

        # Add parent and its children (+ edges) 
        parent_edge = r.inE[0]    
        parent = parent_edge.out
        self.object_drawer.add_object(parent_edge, "e1")
        self.object_drawer.add_object(parent, "n1")

        for parent_child_edge in parent.outE:
            if parent_child_edge.cls == "InformationEdge":
                continue
            self.object_drawer.add_object(parent_child_edge.in_, "n2")
            self.object_drawer.add_object(parent_child_edge, "e2")
        
        # Walk up to root
        while len(parent.inE) > 0:
            e = parent.inE[0]
            parent = e.out
            # Eventually only the edge was fetched but not the node it points to
            if not parent:
                break
            self.object_drawer.add_object(e, "e2")
            self.object_drawer.add_object(parent, "n2")

    def render_graph(self, format = "svg"):
        path = tempfile.mktemp(suffix = ".svg")
        self.render_graph_to_disk(path, format)
        file_content = open(path).readlines()
        os.unlink(path)
        return file_content

    def render_graph_to_disk(self, path, format = "svg"):
        """ Layouts graph and writes is in given format to path """
        self.G.draw(path, format = format, prog = "neato")


class GraphVizObjectDrawer(object):
    def __init__(self, G):
        self.G = G
        self.objects = defaultdict(list)
        self.set_handlers()
    
    def set_handlers(self):    
        # Priority list of drawing handlers
        self.drawing_handlers = [
            ("n_search", self.draw_node_search),
            ("e_search", self.draw_edge_search),
            ("n_root", self.draw_node_root),
            ("e_root", self.draw_edge_root),
            ("n_result", self.draw_node_result),  
            ("e1", self.draw_edge),
            ("e2", self.draw_edge), 
            ("n1", self.draw_node_1),
            ("n2", self.draw_node_2)
        ]

    def add_object(self, o, fmt):
        self.objects[o].append(fmt)
                
    def inject_formats(self):
        """ Adds root format to root nodes and adjacent edges """
        for (o, fmts) in self.objects.iteritems():
            if o.cls == "Root":
                fmts.append("n_root")
            elif o.is_edge and o.out.cls == "Root":
                fmts.append("e_root")
    
    def draw_objects(self):
        self.inject_formats()
        # Bug in pygraphviz? Adding edges before adding their adjacent nodes
        # yields indeterministic results.
        for (o, fmts) in self.objects.iteritems():
            if not o.is_edge:
                self.draw_object(o, fmts)
        for (o, fmts) in self.objects.iteritems():
            if o.is_edge:
                self.draw_object(o, fmts)
            
    def draw_object(self, o, fmts):
            h = next(h for (fmt, h) in self.drawing_handlers
                     if fmt in fmts)
            print o.rid, h.__name__
            h(o)



    ##################################################################
    ## Drawing handlers for edges

    def draw_edge_search(self, e):
        self.draw_edge(e, color = "darkslategrey", style = "dashed")

    def draw_edge_root(self, e):
        self.draw_edge(e, color = "grey")

    def draw_edge(self, e, **kwargs):
        self.add_edge(e.out.rid, e.in_.rid, **kwargs)

    ##################################################################
    ## Drawing handlers for nodes

    def draw_node_search(self, n):
        #html = '<font color="red">%s</font>' % q
        self.add_node(n.rid, n.data["label"],
                      shape = "oval", style = "filled", color = "darkslategrey", fontcolor="white", fontsize = 20)

    def draw_node_result(self, n):   
        url = "show?node_id=%s" % n.rid
        s = '<TABLE CELLBORDER="1" BORDER="0" CELLSPACING="0">'
        s += '<TR><TD BGCOLOR="BLACK"><FONT COLOR="WHITE" POINT-SIZE="20">%s</FONT></TD></TR>' % n.data["label"]
        translations = [e.in_.data["label"] for e in n.outE if e.cls == "InformationEdge" ]
        for t in translations:
            s += '<TR><TD>%s</TD></TR>' % t
        s += '</TABLE>'
                
        self.add_node(n.rid, "<%s>" % s, URL = url, shape = "plaintext")


    def draw_node_root(self, n):
        url = "show?node_id=%s" % n.rid
        html = '<FONT COLOR="GREY" POINT-SIZE="30">%s</FONT>' % n.data["label"]
        self.add_node(n.rid, label = "<%s>" % html, URL = url,
                        shape = "plaintext")
    
    def draw_node_1(self, n):
        url = "show?node_id=%s" % n.rid
        s = '<TABLE CELLBORDER="1" BORDER="0" CELLSPACING="0">'
        s += '<TR><TD BGCOLOR="GREY"><FONT COLOR="WHITE" POINT-SIZE="16">%s</FONT></TD></TR>' % n.data["label"]
        t = next((e.in_.data["label"] for e in n.outE if e.cls == "InformationEdge"), None)
        if t:
            s += '<TR><TD>%s</TD></TR>' % t
        s += '</TABLE>'

        self.add_node(n.rid, label = "<%s>" % s, URL = url, shape = "plaintext")

    def draw_node_2(self, n):
        url = "show?node_id=%s" % n.rid
        s = '<TABLE CELLBORDER="1" BORDER="0" CELLSPACING="0">'
        s += '<TR><TD BGCOLOR="GREY"><FONT COLOR="WHITE" POINT-SIZE="16">%s</FONT></TD></TR>' % n.data["label"]
        s += '</TABLE>'

        self.add_node(n.rid, label = "<%s>" % s, URL = url, shape = "plaintext")
    
    ##################################################################################
    ## For debuggung

    def add_node(self, name, label, **kwargs):
        print "N: %s (%s)" % (name, label)
        self.G.add_node(name, label = label, **kwargs) 

    def add_edge(self, from_, to, **kwargs):
        print "E: %s -> %s" % (from_, to)
        self.G.add_edge(from_, to, **kwargs)


 
if __name__ == '__main__':
    q = u"ألف"
    renderer = GraphvizRenderer()
    renderer.build_graph_for_query(q)
    renderer.render_graph_to_disk("test.svg")       

    renderer = GraphvizRenderer()
    renderer.build_graph_for_node("#14:7015") #Root
    renderer.render_graph_to_disk("test2.svg") 
    
    renderer = GraphvizRenderer()
    renderer.build_graph_for_node("#15:39477")
    renderer.render_graph_to_disk("test1.svg")       

      
