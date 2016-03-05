#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''

class Edge(object):
    pass

class DirectedEdge(object):
    pass

class DerivationEdge(DirectedEdge):
    pass

class VerbDerivationEdge(DerivationEdge):
    pass

class NahtEdge(DerivationEdge):
    """
    https://ar.wikipedia.org/wiki/لفظ_منحوت
    النحت في اللغة، توليد كلمة جديدة بتركيب اثنتين على الأقل
    
    Eventually add Tarkib-Edge, too.
    
    """
    pass


class CollocationEdge(DirectedEdge):
    pass


if __name__ == '__main__':
    pass