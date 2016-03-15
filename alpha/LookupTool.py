#!/usr/bin/env python
# encoding: utf-8
'''

@author:     Mirko Vogel
'''
from Cheetah.Template import Template
import cherrypy

from externaldataproviders import AgglomerationProvider

class LookupTool(object):
    def __init__(self):
        self.agglomeration_provider = AgglomerationProvider()
    
    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("lookup?q=")

    @cherrypy.expose
    def lookup(self, q):
        tmpl = file("web/templates/lookup.tmpl").read().decode("utf-8")
        results = self.agglomeration_provider.query(q)
        t = Template(tmpl, searchList = [{"query": q, "results": results}])
        return unicode(t).encode("utf8")
    
if __name__ == '__main__':
    cherrypy.quickstart(LookupTool(), '/', "cherrypy.conf")