from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from amnesty.shop import shopMessageFactory as _

class IShopItem(Interface):
    """A simple shop item"""
    
    # -*- schema definition goes here -*-
