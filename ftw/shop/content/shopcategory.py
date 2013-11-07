"""Definition of the Shop Category content type
"""

from Acquisition import aq_parent, aq_inner
from Products.Archetypes import atapi
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from zope.interface import implements

try:
    # Plone 4
    from zope.lifecycleevent import ObjectRemovedEvent
except ImportError:
    # Plone 3
    from zope.app.container.contained import ObjectRemovedEvent

from Products.ATContentTypes.config import HAS_LINGUA_PLONE
if HAS_LINGUA_PLONE:
    from Products.LinguaPlone.public import registerType
else:
    from Products.Archetypes.atapi import registerType

from ftw.shop import shopMessageFactory as _
from ftw.shop.interfaces import IShopCategory
from ftw.shop.config import PROJECTNAME
from ftw.shop.content.categorizeable import Categorizeable


ShopCategorySchema = ATFolderSchema.copy() + atapi.Schema((
        atapi.ReferenceField(
            'supplier',
            required = 0,
            languageIndependent=True,
            relationship = 'item_supplier',
            vocabulary_factory="ftw.shop.suppliers_vocabulary",
            widget = atapi.ReferenceWidget(
                label = _(u"label_supplier", default=u"Supplier"),
                description = _(u"desc_supplier", default=u""),
                checkbox_bound = 10,
                ),
            ),
        ))


class ShopCategory(Categorizeable, ATFolder):
    """A category for shop items"""
    implements(IShopCategory)

    meta_type = "ShopCategory"
    schema = ShopCategorySchema

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

registerType(ShopCategory, PROJECTNAME)


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
