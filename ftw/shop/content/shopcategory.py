"""Definition of the Shop Category content type
"""

from Acquisition import aq_parent
from Products.Archetypes import atapi
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from zope.interface import implements

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
        parent_titles = []
        done = False
        while not done:
            parent = aq_parent(parent)
            if parent.portal_type =='ShopCategory':
                parent_titles.append(parent.title)
            else:
                done = True

        parent_titles.append(self.title)
        full_title = " > ".join(parent_titles)
        return full_title

atapi.registerType(ShopCategory, PROJECTNAME)


def object_initialized_handler(context, event):
    """
    @param context: Zope object for which the event was fired for.
    Usually this is Plone content object.

    @param event: Subclass of event.
    """
    parent = aq_parent(context)
    if parent.portal_type == 'ShopCategory':
        context.addToCategory(parent.UID())
