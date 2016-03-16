#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''

from itertools import chain
from pyorient.otypes import OrientRecordLink

import Tools

class WrappedRecord(object):
    """
    Wrapper for pyoreint.otypes.OrientRecord for unicode handling and ease of
    access.
     
    """
    def __init__(self, record):
        """  """
        self.rid = record._OrientRecord__rid
        self.cls = record._OrientRecord__o_class
        self.version = record._OrientRecord__version
        self.data = Tools.decode_map(record.oRecordData)

    @staticmethod
    def from_record(r):
        try:
            if isinstance(r.oRecordData['in'], OrientRecordLink) and \
                    isinstance(r.oRecordData['out'], OrientRecordLink):
                return WrappedEdge(r)
            else:
                return WrappedNode(r)
        except:
            return WrappedNode(r)
        
    def update_links(self, map):
        """
        Replaces OrientRecordLinks with their respective wrapped object. If the
        rid cannot be found in the given map, replaces the link with None.
        
        """
        for (k, v) in self.data.iteritems():
            if isinstance(v, OrientRecordLink):
                self.data[k] =  map.get("#" + v._OrientRecordLink__link)
    
    def __equal__(self, r):
        return self.rid == r.rid

    def __str__(self):
        return unicode(self).encode("utf-8")
    
    @property
    def is_edge(self):
        raise NotImplementedError

    @property
    def is_index_record(self):
        return self.rid == "#-1:-1"

class WrappedNode(WrappedRecord):
    def __init__(self, record):
        """
        Creates a WrappedNode from an OrientRecord, adding the properties
        "in" and "out".
        
        As pyorient does not parse RidBags, the information about incoming and
        outgoing edges is represented by useless OrientBinaryObjects objects.
        We have to reconstruct it from the edges' endpoints, see
        WrappedEdge.update_endpoints().
        
        """
        super(WrappedNode, self).__init__(record)
        # Delete useless OrientBinaryObjects
        for k in self.data.keys():
            if k.startswith("in_") or k.startswith("out_"):
                self.data.pop(k)
                
        self.data["in"] = []
        self.data["out"] = []
        
    def __unicode__(self):
        d = dict(self.data.iteritems())
        in_edges = ", ".join(n.rid for n in d.pop("in"))
        out_edges = ", ".join(n.rid for n in d.pop("out"))
        label = d.pop("label") if "label" in self.data else ""
        return "%s (%s, %s): <-- %s, --> %s, %s" \
                % (self.rid, self.cls, label, in_edges, out_edges, d)

    @property
    def is_edge(self):
        return False

    @property
    def is_orphan(self):
        """ Returns whether there are no adjacent edges """
        return not self.inE and not self.outE

    @property
    def in_(self):
        """Returns adjacent incoming nodes (as iterator)"""
        return (e.out for e in self.inE)
    
    @property
    def out(self):
        """Returns adjacent outgoing nodes"""
        return (e.in_ for e in self.outE)

    @property
    def both(self):
        """Returns adjacent nodes (as iterator)"""
        return chain(self.in_, self.out)

    @property
    def inE(self):
        """Returns adjacent incoming edges"""
        return self.data["in"]
    
    @property
    def outE(self):
        """Returns adjacent outgoing edges"""
        return self.data["out"]

    @property
    def bothE(self):
        """Returns adjacent edges"""
        return chain(self.inE, self.outE)

class WrappedEdge(WrappedRecord):
    def update_links(self, map):
        """
        Replaces OrientRecordLinks with their respective wrapped object. If the
        rid cannot be found in the given map, replaces the link with None.
        
        Updates the connected WrapperNodes to refer to this WrappedEdge object, too.
        (See WrappedNode.__init__)

        """
        super(WrappedEdge, self).update_links(map)
        if self.in_:
            self.in_.inE.append(self)
        if self.out:
            self.out.outE.append(self)

    def __unicode__(self):
        d = dict(self.data.iteritems())
        in_ = d.pop("in").rid if self.in_ else None
        out = d.pop("out").rid if self.out else None
        return "%s (%s): %s --> %s, %s" \
                % (self.rid, self.cls, in_, out, Tools.encode_map(d))

    @property
    def is_edge(self):
        return True
        
    @property
    def in_(self):
        """Returns adjacent incoming node"""
        return self.data["in"]

    @property
    def out(self):
        """Returns adjacent outgoing node"""
        return self.data["out"]
     
if __name__ == '__main__':
    pass