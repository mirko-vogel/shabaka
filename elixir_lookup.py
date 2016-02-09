#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Jan 20, 2016

@author: mirko
'''


import sys
import json
import pygraphviz as pgv
from collections import defaultdict

class LexiconEntry:
    ROMAN_TO_INT = defaultdict(int, {
        "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6,
        "VII": 7, "VIII": 8, "IX": 9, "X": 10})
    
    def __init__(self, citation_form, entry_type, root, pattern, stem,
                 translations, metadata = None):
        """
        Create an Arabic lexicon entry:
        - citation_form: unicode string
        - entry_type: string, e.g. "A"
        - root: unicode string consisting of root letters (not space separated)
        - pattern: str, e.g.FAiL
        - stem: integer 0..10, 0 stands for no-stem
        - translations: array of strings
        - metadata: dictionary
        
        """
        self.citation_form = citation_form
        self.entry_type = entry_type
        self.root = root
        self.pattern = pattern
        self.stem = stem
        self.translations = translations
        if not metadata:
            metadata = {}
        self.metadata = metadata

    @staticmethod
    def from_elixirfm_json(data):
        if len(data) > 2:
            # FIXME
            # For Verbs: Imperative form (imperfect vocal), Masdar
            # For Nous: Plural forms
            # Feminine froms?
            additional_info = data[2:]
        entry_id, data = data[0], data[1]
        entry_type, data = data[0].strip("-"), data[1]
        citation_form, data = data[0], data[1]
        # We want the root to be a unicode string without spaces
        root, data = "".join(data[0].split()), data[1]
        pattern, data = data[0], data[1]
        translation, data = data[0], data[1]
        translations = str(translation).translate(None, "\"][").split(",")
        # If no stem info is given, use 0
        stem = LexiconEntry.ROMAN_TO_INT[data[1:-1]]
        
        node = LexiconEntry(citation_form, entry_type, root, pattern, stem, translations)
        return node

    def get_surface_forms(self):
        """
        Returns an array of surface form one could use to search for the lexicon
        entry, e.g. plural, feminine, etc.
        
        """
        # IMPLEMENT ME
        return [self.citation_form]


    def __unicode__(self):
        return "%s (%s): %s" % (self.citation_form, self.entry_type,
                                 ", ".join(self.translations)) 

    @property
    def is_verb(self):
        return self.entry_type == "V"

class Lexicon:
    def __init__(self):
        # Array of LexiconEntry objects
        self.entries = []
        # Set of known roots
        self.roots = set([])
        # Dictionary: vocalized surface form -> array of LexiconEntry objects
        #   populated with plural, feminine forms, etc., too
        self.entries_by_surface_form = defaultdict(list)

    def import_dump(self, fn):
        raw = json.load(open(fn), "utf-8")
        
        def flatten(a):
            if type(a) == unicode:
                return a
            a = map(flatten, a)
            if len(a) == 1:
                return a[0]
            return a 
        
        raw = flatten(raw)
        for r in raw:
            root_id = str(r[0]).translate(None, "()[],")
            derivations = r[1][1:]
            for e in derivations:
                try:
                    entry = LexiconEntry.from_elixirfm_json(e)
                    print unicode(entry)
                    self.add_entry(entry)
                except:
                    print "Error parsing derivation from root id %s", root_id
                    
    def add_entry(self, entry):
        """
        Add lexicon entry to lexicon. Updates "lookup table" 
        entries_by_surface_form.
        
        """
        self.entries.append(entry)
        self.roots.add(entry.root)
        for s in entry.get_surface_forms():
            self.entries_by_surface_form[s].append(entry)
        

class LexiconNode(object):
    NODE_ATTRIBUTES = {"shape": "plaintext"}
    
    def __init__(self, entry, edges = None):
        self.entry = entry
        self.edges = edges
        if not self.edges:
            self.edges = []
        
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
        if cur_dist <= max_dist:
            for e in self.edges:
                e.otherside(self).draw_neighbourhood(G, cur_dist + 1, max_dist,
                                                     already_drawn)
                e.draw(G, cur_dist + 1, already_drawn)
                
    def draw(self, G, cur_dist, already_drawn):
        """ Draws node if not already drawn, updates already drawn list """
        if self in already_drawn:
            return
        
        G.add_node(hash(self), label = "<%s>" % self.get_node_label(cur_dist),
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

class StemNode(LexiconNode):
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
            n = LexiconNode(e)
            e = DirectedLexiconEdge(stem_node, n, e.entry_type)
            nodes.append(n)
            edges.append(e)
        
        return nodes, edges

    
class RootNode(LexiconNode):
    NODE_ATTRIBUTES = {"color": "grey"}
    
    """ Represent a root, does not carry a lexicon entry """
    def __init__(self, root, edges = None):
        self.root = root
        self.edges = edges
        if not self.edges:
            self.edges = []
    
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
                new_edges.append(DirectedLexiconEdge(root_node, stem_node, stem))
            else:
                # Others connect directly to root
                new_nodes = [LexiconNode(e) for e in stem_entries]
                new_edges = [DirectedLexiconEdge(root_node, n) for n in new_nodes]
            
            nodes += new_nodes
            edges += new_edges
            
        return nodes, edges    
             
    def get_node_label(self, cur_dist):
        r = " ".join(self.root)
        return '<FONT COLOR="GREY" POINT-SIZE="20">%s</FONT>' % r
            

class DirectedLexiconEdge(object):
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


class LexiconGraph:
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
        G = pgv.AGraph(**LexiconGraph.GRAPHVIZ_PARAMS)
        center_node.draw_neighbourhood(G, 0, max_dist)
        return G

fn = sys.argv[1]
l = Lexicon()
l.import_dump(fn)
lg = LexiconGraph(l)
G = lg.draw(lg.nodes[14], 2)
#engines = ("dot", "neato", "sfdp", "fdp", "twopi", "circo")
engines = ("neato", )
for engine in engines:
    G.layout(prog = engine)
    print G.string()
    G.draw("%s.svg" % engine)


 

