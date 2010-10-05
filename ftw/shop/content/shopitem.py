"""Definition of the Shop Item content type
"""

from zope.interface import implements, alsoProvides

from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema

from ftw.shop.interfaces.shopitem import IShopItem
from ftw.shop.interfaces import IShoppable
from ftw.shop.content.categorizeable import Categorizeable
from ftw.shop.config import PROJECTNAME


from Products.ATContentTypes.config import HAS_LINGUA_PLONE
if HAS_LINGUA_PLONE:
    from Products.LinguaPlone.public import registerType
else:
    from Products.Archetypes.atapi import registerType

ShopItemSchema = ATFolderSchema.copy() 

class ShopItem(Categorizeable, ATFolder):
    """A simple shop item"""
    implements(IShopItem)
    alsoProvides(IShoppable)

    meta_type = "ShopItem"
    schema = ShopItemSchema


registerType(ShopItem, PROJECTNAME)
