from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from amnesty.shop import shopMessageFactory as _

class IShopMultiItem(Interface):
    """A shop item that consists of multiple variants (eg. colors, sizes)"""
    
    # -*- schema definition goes here -*-
