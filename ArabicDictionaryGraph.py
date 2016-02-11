#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Jan 20, 2016

@author: mirko
'''


import sys
import pygraphviz as pgv
from collections import defaultdict

from ArabicDictionary import ArabicDictionary

class DictionaryNodeBase(object):
    last_id = 0

    def __init__(self, edges = None):
        self.edges = edges
        if not self.edges:
            self.edges = []
  
        self.id = DictionaryNode.last_id
        DictionaryNode.last_id += 1

class DictionaryNode(DictionaryNodeBase):
    NODE_ATTRIBUTES = {"shape": "plaintext"}
    
    def __init__(self, entry, edges = None):
        DictionaryNodeBase.__init__(self, edges)
        self.entry = entry
              
        # Maybe not an elegant solution ...
        self.entry.metadata["node"] = self

    def draw_neighbourhood(self, G, cur_dist, max_dist, already_drawn = None):
        """
        Recursively adds nodes and connecting edges to graph which have not
        already been drawn. cur_dist is the distance from the center node,
        affecting the level of detail with which the current node is drawn.
        Nodes further away than max_dist are ommitted.
         
        """
        if already_drawn == None:
            already_drawn = set()
        
        if self in already_drawn:
            return
        
        self.draw(G, cur_dist, already_drawn)
        if cur_dist < max_dist:
            for e in self.edges:
                e.otherside(self).draw_neighbourhood(G, cur_dist + 1, max_dist,
                                                     already_drawn)
                e.draw(G, cur_dist + 1, already_drawn)
                
    def draw(self, G, cur_dist, already_drawn):
        """ Draws node if not already drawn, updates already drawn list """
        if self in already_drawn:
            return
        
        G.add_node(hash(self), label = "<%s>" % self.get_node_label(cur_dist), URL = "show?node_id=%s" % self.id,
                   **self.NODE_ATTRIBUTES)
        already_drawn.add(self)
        
    def get_node_label(self, cur_dist):
        """
        Get HTML-like node label, with details depending on the current distance
        from the center node.
        
        The center node itset (dist = 0) has all details, the adjacent ones
        have a limited set, the other one no details.
        
        """
        s = '<TABLE CELLBORDER="1" BORDER="0" CELLSPACING="0">'
        
        if cur_dist == 0:
            # Center node, all details
            s += '<TR><TD BGCOLOR="BLACK"><FONT COLOR="WHITE" POINT-SIZE="20">%s</FONT></TD></TR>' % self.entry.citation_form
            for t in self.entry.translations:
                s += '<TR><TD>%s</TD></TR>' % t
        elif cur_dist == 1:
            # Adjacent nodes, only one translation
            s += '<TR><TD BGCOLOR="GREY"><FONT COLOR="WHITE" POINT-SIZE="16">%s</FONT></TD></TR>' % self.entry.citation_form
            s += '<TR><TD>%s</TD></TR>' % self.entry.translations[0]            
        else:
            # Other nodes: No translations
            s += '<TR><TD BGCOLOR="GREY"><FONT COLOR="WHITE" POINT-SIZE="14">%s</FONT></TD></TR>' % self.entry.citation_form
        
        s += '</TABLE>'
        return s

class StemNode(DictionaryNode):
    NODE_ATTRIBUTES = {"shape": "plaintext"}
    
    @staticmethod
    def create_graph(entries):
        """
        Creates graph consisting of entries derived from the same stem
        Return tuple (created nodes, created edges)
        
        """
        verb_entry = next(e for e in entries if e.is_verb)
        stem_node = StemNode(verb_entry)
        nodes, edges = [stem_node], []

        for e in entries:
            if e.is_verb:
                continue
            n = DictionaryNode(e)
            e = DirectedEdge(stem_node, n, e.entry_type)
            nodes.append(n)
            edges.append(e)
        
        return nodes, edges

    
class RootNode(DictionaryNode):
    NODE_ATTRIBUTES = {"color": "grey"}
    
    """ Represent a root, does not carry a lexicon entry """
    def __init__(self, root, edges = None):
        DictionaryNodeBase.__init__(self, edges)
        self.root = root
    
    @staticmethod
    def create_graph(root, entries):
        """
        Create a graph for given root and associated entries.
        The root connects to the verb stems and all entries not
        carrying stem information. Entries carrying stem information
        connect to their respective stem.
        
        """
        root_node = RootNode(root)
        nodes, edges = [root_node], []
        
        entries_by_stem = defaultdict(list)
        for e in entries:
            entries_by_stem[e.stem].append(e)
        
        for (stem, stem_entries) in entries_by_stem.iteritems():
            if stem > 0:
                # Subgraphs by verb stem are handled be StemNode
                new_nodes, new_edges = StemNode.create_graph(stem_entries)
                stem_node = next(n for n in new_nodes if type(n) == StemNode)
                new_edges.append(DirectedEdge(root_node, stem_node, stem))
            else:
                # Others connect directly to root
                new_nodes = [DictionaryNode(e) for e in stem_entries]
                new_edges = [DirectedEdge(root_node, n) for n in new_nodes]
            
            nodes += new_nodes
            edges += new_edges
            
        return nodes, edges    
             
    def get_node_label(self, cur_dist):
        r = " ".join(self.root)
        return '<FONT COLOR="GREY" POINT-SIZE="20">%s</FONT>' % r
            

class DirectedEdge(object):
    def __init__(self, source, target, label = ""):
        """
        Create a directed lexicon edge, adding itself to source and target 
        node edge list automatically
        
        """
        self.source = source
        self.source.edges.append(self)
        self.target = target
        self.target.edges.append(self)
        
        self.label = label
        
    def otherside(self, n):
        """
        Returns the other side of the edge, given one side.
        Raises an IndexError if n is not an adjacent node.
        
        """
        if n == self.source:
            return self.target
        elif n == self.target:
            return self.source
        else:
            raise IndexError

    def draw(self, G, cur_dist, already_drawn):
        """ Draws edge if not already drawn, updates already drawn list """
        if self in already_drawn:
            return
        
        # NICER DRAWING
        G.add_edge(hash(self.source),
                   hash(self.target), label = self.label)
        already_drawn.add(self)


class ArabicDictionaryGraph:
    GRAPHVIZ_PARAMS = {"directed": True, "overlap": "scale"}
    
    def __init__(self, lexicon):
        """ Create a LexiconGraph from a Lexicon """
        self.lexicon = lexicon
        self.nodes = []
        self.edges = []
        
        self.__create_graph()

    def __create_graph(self):
        entries_by_roots = defaultdict(list)
        for e in self.lexicon.entries:
            entries_by_roots[e.root].append(e)

        for (root, entries) in entries_by_roots.iteritems():
            nodes, edges = RootNode.create_graph(root, entries)
            self.nodes += nodes
            self.edges += edges
    
    def draw(self, center_node, max_dist = 3):
        G = pgv.AGraph(**ArabicDictionaryGraph.GRAPHVIZ_PARAMS)
        center_node.draw_neighbourhood(G, 0, max_dist)
        return G

if __name__ == '__main__':
    fn = sys.argv[1]
    l = ArabicDictionary()
    l.import_dump(fn)
    lg = ArabicDictionaryGraph(l)
    G = lg.draw(lg.nodes[3], 2)
    #engines = ("dot", "neato", "sfdp", "fdp", "twopi", "circo")
    engines = ("neato", )
    open("graph.dot", "w").write(G.string().encode("utf-8"))
    for engine in engines:
        G.layout(prog = engine)
        G.draw("%s.svg" % engine)
    
    
 

