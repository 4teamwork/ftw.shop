"""Definition of the Shop Item content type
"""

from Acquisition import aq_parent
from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.document import ATDocumentSchema
from zope.interface import implements, alsoProvides

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

from ftw.shop.interfaces import IShopItem, IBuyable
from ftw.shop.content.categorizeable import Categorizeable
from ftw.shop.config import PROJECTNAME

ShopItemSchema = ATDocumentSchema.copy()
ShopItemSchema["description"].widget.visible = {"edit": "invisible" }

class ShopItem(Categorizeable, ATDocument):
    """A simple shop item"""
    implements(IShopItem)
    alsoProvides(IBuyable)

    meta_type = "ShopItem"
    schema = ShopItemSchema

    def __bobo_traverse__(self, REQUEST, name):
        """Give transparent access to image scales. This hooks into the
        low-level traversal machinery, checking to see if we are trying to
        traverse to /path/to/object/image_<scalename>, and if so, returns
        the appropriate image content.
        """
        if name.startswith('image'):
            field = self.getField('image')
            image = None
            if name == 'image':
                image = field.getScale(self)
            else:
                scalename = name[len('image_'):]
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename)

            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image

        return super(ShopItem, self).__bobo_traverse__(REQUEST, name)


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
