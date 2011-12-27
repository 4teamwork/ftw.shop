"""Definition of the Shop Item content type
"""

from Acquisition import aq_parent
from Products.Archetypes import atapi
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.configuration import zconf

from zope.interface import implements, alsoProvides
from zope.lifecycleevent import ObjectRemovedEvent

from Products.ATContentTypes.config import HAS_LINGUA_PLONE
if HAS_LINGUA_PLONE:
    from Products.LinguaPlone.public import registerType
else:
    from Products.Archetypes.atapi import registerType

from ftw.shop.interfaces import IShopItem, IBuyable
from ftw.shop.content.categorizeable import Categorizeable
from ftw.shop.config import PROJECTNAME
from ftw.shop import shopMessageFactory as _


ShopItemSchema = ATContentTypeSchema.copy() + atapi.Schema((
    atapi.TextField('text',
        required=False,
        searchable=True,
        primary=True,
        storage=atapi.AnnotationStorage(migrate=True),
        default_output_type='text/x-html-safe',
        widget=atapi.RichWidget(
            description='',
            label=_(u'label_body_text', default=u'Body Text'),
            rows=25,
            allow_file_upload = zconf.ATDocument.allow_document_upload),
        ),
))


class ShopItem(Categorizeable, ATCTContent):
    """A simple shop item"""
    implements(IShopItem)
    alsoProvides(IBuyable)

    meta_type = "ShopItem"
    schema = ShopItemSchema


def add_to_containing_category(context, event):
    """
    @param context: Zope object for which the event was fired for.
    Usually this is Plone content object.

    @param event: Subclass of event.
    """

    if not event.__class__ ==  ObjectRemovedEvent:
        parent = aq_parent(context)
        context.addToCategory(parent.UID())

registerType(ShopItem, PROJECTNAME)
