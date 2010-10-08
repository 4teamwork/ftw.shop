"""Definition of the Shop Item content type
"""

from zope.interface import implements, alsoProvides

from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.document import ATDocumentSchema

from ftw.shop.interfaces.shopitem import IShopItem
from ftw.shop.interfaces import IBuyable
from ftw.shop.content.categorizeable import Categorizeable
from ftw.shop.config import PROJECTNAME
from Acquisition import aq_parent


from Products.ATContentTypes.config import HAS_LINGUA_PLONE
if HAS_LINGUA_PLONE:
    from Products.LinguaPlone.public import registerType
else:
    from Products.Archetypes.atapi import registerType

ShopItemSchema = ATDocumentSchema.copy() 

class ShopItem(Categorizeable, ATDocument):
    """A simple shop item"""
    implements(IShopItem)
    alsoProvides(IBuyable)

    meta_type = "ShopItem"
    schema = ShopItemSchema

def object_initialized_handler(context, event):
    """
    @param context: Zope object for which the event was fired for. Usually this is Plone content object.

    @param event: Subclass of event.
    """
    parent = aq_parent(context)
    context.addToCategory(parent.UID())

registerType(ShopItem, PROJECTNAME)
