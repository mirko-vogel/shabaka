#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Mar 12, 2016

@author: mirko
'''
from awg import ArabicWordGraph
from ArabicDictionary import ArabicDictionary, ArabicDictionaryEntry
from collections import defaultdict

class Importer(object):
    def __init__(self, graph = None):
        if not graph:
            graph = ArabicWordGraph()
        self.graph = graph
        ## map (translation, pos) -> OrientRecord
        self.added_translations = {}
        
    def import_json_file(self, fn, skip_to = 1):
        """
        Import ElixirFM lexicon from json file, optionally skipping the first
        skip_to roots. This index is 1-based.
        """
        d = ArabicDictionary()
        d.import_dump(fn)
    
        entries_by_roots = defaultdict(list)
        for e in d.entries:
            entries_by_roots[e.root].append(e)
    
        N = len(entries_by_roots)
        for (n, (root, entries)) in enumerate(entries_by_roots.iteritems()):
            if n + 1 < skip_to:
                continue
            sys.stdout.write("\rImporting root %d/%d" % (n + 1, N))
            try:
                self.import_root(root, entries)
            except RuntimeError as e:
                sys.stderr.write("Error while importing root %s: %s\n" % (root, e))
    
    def add_translations(self, node, pos, translations):
        """
        Adds translations of the word represented by node by connecting it to
        suitable ForeignWordNodes, eventually creating them. A translation is
        characterized by its surface form and its pos.
        
         """
        metadata = {"source": "elixirfm", "pos": pos,
                    "source_link": "http://quest.ms.mff.cuni.cz/cgi-bin/elixir"}

        for t in translations:
            try:
                v = self.added_translations[(t, pos)]
                self.graph.create_edge("informationedge", node, v)
            except:
                n = self.graph.add_foreign_node(t, "en", node, metadata)
                self.added_translations[(t, pos)] = n
    
                
    def import_root(self, root, entries):
        """
        Create a graph for given root and associated entries.
        The root connects to the verb stems and all entries not
        carrying stem information. Entries carrying stem information
        connect to their respective stem.
        
        """
        root_node = self.graph.add_root_node(" ".join(root))
        
        entries_by_stem = defaultdict(list)
        stemless_entries = []
        for e in entries:
            if e.stem:
                entries_by_stem[e.stem].append(e)
            else:
                stemless_entries.append(e)
        
        # Import stems, build hierarchy below verb and store created noun nodes
        created_noun_nodes = []
        for (stem, stem_entries) in entries_by_stem.iteritems():
            created_noun_nodes += self.import_stem(root_node, stem_entries)
            
        self.add_nouns(stemless_entries, created_noun_nodes, root_node)
                    
    
    def import_stem(self, root_node, entries):
        """
        Creates graph consisting of entries derived from the same stem
        Return a list of created noun nodes.
        
        TODO: Deal with several verbs: استجاب / استجوب
        """
        # Step 1: Create verb nodes for verbs
        verb_entries = [e for e in entries if e.is_verb]
        if not verb_entries:
            verb_entries.append(ArabicDictionaryEntry("", "V", entries[0].root, "",
                                                      entries[0].stem, []))
            print "Invented verb of stem %s of root %s" % (e.stem, e.root) 
        
        verb_nodes = []
        for e in verb_entries: 
            v = self.graph.add_verb_node(e.citation_form, e.stem, root_node,
                                            {"pattern": e.pattern, "elixir_id": e.entry_id})
            self.add_translations(v, e.entry_type, e.translations)
            verb_nodes.append(v)
    
        # HACK: use first verb node
        verb_node = verb_nodes[0]

        # Add remaining nodes - must be nouns
        created_noun_nodes = []
        self.add_nouns(entries, created_noun_nodes, verb_node)
        return created_noun_nodes


    def add_nouns(self, entries, created_noun_nodes, fallback_node):
        """
        Adds noun nodes for the given entries connecting them by
        NounDerivationEdges to the most suitable parents. Potential parents are
        the noun nodes created from the given entries, the nodes passed as
        created_noun_nodes and the fallback_node.
        
        Entries that are verbs are ignored.
        
        The nodes added to the Graph are added to created_noun_nodes, too.

        """        
        # Classify words according to pattern components
        remaining_entries_by_pattern = [defaultdict(list) for i in range(5)]
        for e in entries:
            if e.is_verb:
                continue
            l = e.pattern.count(" |< ")
            remaining_entries_by_pattern[l][e.pattern].append(e)
                    
        for entry_group in remaining_entries_by_pattern:
            for (pattern, entries) in entry_group.iteritems():
                # Look for parent
                parent = next((p for p in reversed(created_noun_nodes)
                              if pattern.find(p.data["pattern"]) >= 0),
                              fallback_node)
                n = self.graph.add_noun_node(entries[0].citation_form, parent,
                                             {"pattern": pattern, "elixir_id": e.entry_id})
                created_noun_nodes.append(n)
                for e in entries:
                    self.add_translations(n, e.entry_type, e.translations)

import codecs, sys, os
sys.stderr = codecs.getwriter('utf-8')(os.fdopen(sys.stderr.fileno(), 'w', 0), "delete")
sys.stdout = codecs.getwriter('utf-8')(os.fdopen(sys.stdout.fileno(), 'w', 0), "replace")

if __name__ == "__main__":
    importer = Importer()
    importer = importer.import_json_file(sys.argv[1], skip_to = 5900)
