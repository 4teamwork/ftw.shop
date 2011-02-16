"""Definition of the Shop Category content type
"""

from Acquisition import aq_parent, aq_inner
from Products.Archetypes import atapi
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from zope.interface import implements
from zope.lifecycleevent import ObjectRemovedEvent

from ftw.shop.interfaces import IShopCategory
from ftw.shop.config import PROJECTNAME
from ftw.shop.content.categorizeable import Categorizeable


class ShopCategory(Categorizeable, ATFolder):
    """A category for shop items"""
    implements(IShopCategory)

    meta_type = "ShopCategory"
    schema = ATFolderSchema.copy()

    def fullTitle(self):
        """Returns a fully qualified title for the category, including
        parent categories' titles if applicable.
        """
        parent = self
        title_chain = []
        while parent.portal_type =='ShopCategory':
            title_chain.append(parent.Title())
            parent = aq_parent(aq_inner(parent))
        title_chain.reverse()
        return title_chain

atapi.registerType(ShopCategory, PROJECTNAME)


def add_to_containing_category(context, event):
    """
    @param context: Zope object for which the event was fired for.
    Usually this is Plone content object.

    @param event: Subclass of event.
    """
    if not event.__class__ ==  ObjectRemovedEvent:
        parent = aq_parent(context)
        if parent.portal_type == 'ShopCategory':
            context.addToCategory(parent.UID())
