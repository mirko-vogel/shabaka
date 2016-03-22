#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''

import cherrypy
from awg import ArabicWordGraph
from externaldataproviders import AgglomerationProvider

class WebInterface(object):
    """
    
    """
    def __init__(self, graph = None):
        if not graph:
            graph = ArabicWordGraph()
        self.graph = graph
        self.agglomeration_provider = AgglomerationProvider()

    @cherrypy.expose
    def index(self):
        raise NotImplementedError

    @cherrypy.expose
    def search(self, q):
        raise NotImplementedError
    
    @cherrypy.expose
    def show(self, rid):
        raise NotImplementedError

