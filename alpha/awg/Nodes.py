#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: mirko
'''

class Node(object):
    """
    Base class for all Node objects
    """
    external_data_providers = []

    @property
    def label(self):
        raise NotImplementedError
    
    def __str__(self):
        return unicode(self).encode('utf-8')
    
    def __unicode__(self):
        return self.label


class RootNode(Node):
    """
    Could carry ElixirFM root id
    
    """
    pass

class VerbNode(Node):
    """
    
    """
    pass
    
class IsmNode(Node):
    pass

if __name__ == '__main__':
    pass