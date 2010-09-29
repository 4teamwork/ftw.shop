"""Definition of the Shop Item content type
"""

from zope.interface import implements, alsoProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from ftw.shop import shopMessageFactory as _
from ftw.shop.interfaces.shopitem import IShopItem
from ftw.shop.interfaces import IShoppable
from ftw.shop.content.categorizeable import Categorizeable
from ftw.shop.config import PROJECTNAME


ShopItemSchema = ATFolderSchema.copy() 

class ShopItem(Categorizeable, ATFolder):
    """A simple shop item"""
    implements(IShopItem)
    alsoProvides(IShoppable)

    meta_type = "ShopItem"
    schema = ShopItemSchema

atapi.registerType(ShopItem, PROJECTNAME)
