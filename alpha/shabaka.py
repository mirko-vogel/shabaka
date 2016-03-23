#!/usr/bin/env python
# encoding: utf-8
'''

@author:     Mirko Vogel
'''

import cherrypy
import os.path

from webinterface import TextWebInterface, GraphvizWebInterface

server_conf = {"server.socket_host": "0.0.0.0",
               "server.socket_port":  8080 }

css_path = os.path.join(os.path.dirname(__file__), "web", "static", "main.css")
app_conf = {
    "/static/main.css": {
        "tools.staticfile.on": True,
        "tools.staticfile.filename": css_path
    }}


if __name__ == '__main__':
    tx = TextWebInterface()
    gw = GraphvizWebInterface()
    # Let them share an AgglomerationProvider to share its cache
    tx.agglomeration_provider = gw.agglomeration_provider

    cherrypy.config.update(server_conf)
    cherrypy.tree.mount(tx, '/tx', "cherrypy.conf")
    cherrypy.tree.mount(gw, '/gw', "cherrypy.conf")
    cherrypy.engine.start()
    cherrypy.engine.block()