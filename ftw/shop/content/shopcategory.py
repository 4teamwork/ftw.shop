"""Definition of the Shop Category content type
"""

from Acquisition import aq_parent

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema

from ftw.shop.interfaces import IShopCategory
from ftw.shop.config import PROJECTNAME
from ftw.shop.content.categorizeable import Categorizeable


class ShopCategory(Categorizeable, ATFolder):
    """A category for shop items"""
    implements(IShopCategory)

    meta_type = "ShopCategory"
    schema = ATFolderSchema.copy()

atapi.registerType(ShopCategory, PROJECTNAME)

def object_initialized_handler(context, event):
    """
    @param context: Zope object for which the event was fired for. Usually this is Plone content object.

    @param event: Subclass of event.
    """
    parent = aq_parent(context)
    if parent.portal_type == 'ShopCategory':
        context.addToCategory(parent.UID())