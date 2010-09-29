"""Definition of the Shop Item Variant content type
"""

from zope.interface import implements, alsoProvides

from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content import schemata
from ftw.shop.interfaces.shopitemvariant import IShopItemVariant
from ftw.shop.config import PROJECTNAME
from ftw.shop.content.shopitem import ShopItemSchema

from ftw.shop.interfaces import IShoppable

from Products.ATContentTypes.config import HAS_LINGUA_PLONE
if HAS_LINGUA_PLONE:
    from Products.LinguaPlone.public import registerType
else:
    from Products.Archetypes.atapi import registerType


ShopItemVariantSchema = ShopItemSchema.copy() 

schemata.finalizeATCTSchema(ShopItemVariantSchema, moveDiscussion=False)

class ShopItemVariant(ATFolder):
    """A shop item variant for multi items"""
    implements(IShopItemVariant)
    alsoProvides(IShoppable)

    meta_type = "ShopItemVariant"
    schema = ShopItemVariantSchema

registerType(ShopItemVariant, PROJECTNAME)
