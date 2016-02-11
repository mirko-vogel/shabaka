#!/usr/bin/env python
# encoding: utf-8
'''
Bla bal

@author:     Mirko Vogel
'''
import sys, os

import cherrypy, cherrypy.lib.static
import tempfile

from ArabicDictionary import ArabicDictionary
from ArabicDictionaryGraph import ArabicDictionaryGraph

TEMPLATE = """
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <title>Arabic Graph - %s</title>
</head>
<body>
  %s
</body
</html>
"""

class ArabicDictionaryServer(object):
    def __init__(self, adg):
        self.adg = adg
        
    @cherrypy.expose
    def index(self):
        '''
        '''
        return 'What up, yo?'

    @cherrypy.expose
    def show(self, node_id):
        """Returns html page with embeded svg"""

        center_node = self.adg.nodes[int(node_id)]
        G = self.adg.draw(center_node, 2)
        
        path = tempfile.mktemp(suffix = ".svg")
        G.draw(path, format = "svg", prog = "neato")
        svg_lines = open(path).readlines()
        os.unlink(path)
        
        svg = "\n".join(svg_lines[6:])
        entry = unicode(center_node.entry).encode("utf-8")
        s = TEMPLATE % (entry, svg)
        return s

    
conf = {
    'global': {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8080
    }
}

if __name__ == '__main__':
    l = ArabicDictionary()
    l.import_dump(sys.argv[1])
    adg = ArabicDictionaryGraph(l)
    server = ArabicDictionaryServer(adg)
    
    cherrypy.quickstart(server, '/', conf)