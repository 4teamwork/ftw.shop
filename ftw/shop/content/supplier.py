from Products.ATContentTypes.content import base
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.Archetypes import atapi
from Products.Archetypes.Widget import TextAreaWidget
from ftw.shop import shopMessageFactory as _
from ftw.shop.config import PROJECTNAME
from ftw.shop.interfaces import ISupplier
from zope.interface import implements


from Products.ATContentTypes.config import HAS_LINGUA_PLONE
if HAS_LINGUA_PLONE:
    from Products.LinguaPlone.public import registerType
else:
    from Products.Archetypes.atapi import registerType


SupplierSchema = ATContentTypeSchema.copy() + atapi.Schema((

        atapi.TextField(
            name='email',
            required=True,
            label=_(u'label_supplier_email', default=u"E-Mail")),

        atapi.TextField(
            name='address',
            required=False,

            widget=TextAreaWidget(
                label=_(u'label_supplier_address', default=u"Address"),
                description=_(u'help_supplier_address',
                              default=u"Supplier's postal address")))))


SupplierSchema['title'].widget.label = _(u"label_name", default="Name")
SupplierSchema['title'].widget.description = _(u"help_name",
                                               default="The supplier's name")

SupplierSchema['description'].widget.visible = {'edit': 'invisible',
                                                'view': 'invisible'}


class Supplier(base.ATCTContent):
    """A supplier
    """
    implements(ISupplier)

    meta_type = "Supplier"
    schema = SupplierSchema

registerType(Supplier, PROJECTNAME)
