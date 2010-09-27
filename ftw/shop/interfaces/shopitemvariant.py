from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from ftw.shop import shopMessageFactory as _

class IShopItemVariant(Interface):
    """A shop item variant for multi items"""
    
    # -*- schema definition goes here -*-
