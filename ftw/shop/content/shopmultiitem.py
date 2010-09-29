"""Definition of the Shop Multi Item content type
"""

from zope.interface import implements
from Products.Archetypes import atapi
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from ftw.shop.interfaces.shopmultiitem import IShopMultiItem
from ftw.shop.content.categorizeable import Categorizeable
from ftw.shop.config import PROJECTNAME

ShopMultiItemSchema = ATFolderSchema.copy()


class ShopMultiItem(Categorizeable, ATFolder):
    """A shop item that consists of multiple variants (eg. colors, sizes)"""
    implements(IShopMultiItem)

    meta_type = "ShopMultiItem"
    schema = ShopMultiItemSchema

atapi.registerType(ShopMultiItem, PROJECTNAME)
