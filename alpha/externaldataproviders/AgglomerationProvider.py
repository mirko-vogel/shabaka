#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''

from externaldataproviders import ALL_PROVIDERS

class AgglomerationProvider(object):
    """Helper class to query all known providers at a time """
    def __init__(self):
        self.providers = [P() for P in ALL_PROVIDERS]

    def query(self, query_string):
        """ Returns a list of results, one for every known provider. """
        return [P.query(query_string) for P in self.providers]
