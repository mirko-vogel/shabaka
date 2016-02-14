'''
Created on Feb 9, 2016

@author: mirko
'''

import json
from collections import defaultdict
from pyarabic import araby

class ArabicDictionaryEntry:
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
        stem = ArabicDictionaryEntry.ROMAN_TO_INT[data[1:-1]]
        
        node = ArabicDictionaryEntry(citation_form, entry_type, root, pattern, stem, translations)
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

class ArabicDictionary:
    def __init__(self):
        # Array of ArabicDictionaryEntry objects
        self.entries = []
        # Set of known roots
        self.roots = set([])
        # Dictionary: vocalized surface form -> array of ArabicDictionaryEntry objects
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
                    entry = ArabicDictionaryEntry.from_elixirfm_json(e)
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
            # Add vocalized and non-vocalized forms
            self.entries_by_surface_form[s].append(entry)
            self.entries_by_surface_form[araby.strip_tashkeel(s)].append(entry)
        
    def search(self, citation_form):
        """
        Seach for given citation form. If not found try again without diacritcs.
        
        Returns a list of ArabicDictionaryEntries. 
        """
        if citation_form not in self.entries_by_surface_form:
            citation_form = araby.strip_tashkeel(citation_form)

        try:
            return self.entries_by_surface_form[citation_form]
        except IndexError:
            return []
        
        
        