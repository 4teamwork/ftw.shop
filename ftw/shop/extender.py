from zope.component import adapts
from zope.interface import implements

from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender
from Products.Archetypes import atapi

from Products.ATContentTypes.config import HAS_LINGUA_PLONE
if HAS_LINGUA_PLONE:
    from Products.LinguaPlone.public import BooleanField
    from Products.LinguaPlone.public import StringField
    from Products.LinguaPlone.public import LinesField
    from Products.LinguaPlone.public import FixedPointField
else:
    from Products.Archetypes.atapi import BooleanField
    from Products.Archetypes.atapi import StringField
    from Products.Archetypes.atapi import LinesField
    from Products.Archetypes.atapi import FixedPointField

from ftw.shop import shopMessageFactory as _
from ftw.shop.interfaces import IShopItem


class ExtBooleanField(ExtensionField, BooleanField):
    """A boolean field."""


class ExtStringField(ExtensionField, StringField):
    """A string field."""


class ExtFixedPointField(ExtensionField, FixedPointField):
    """A fixed point field."""


class ExtLinesField(ExtensionField, LinesField):
    """A lines field."""


class ShopItemExtender(object):
    """Extends the base type ShopItem with fields `price`
    and `skuCode`.
    """
    implements(ISchemaExtender)
    adapts(IShopItem)


    fields = [
        ExtFixedPointField('price',
            default = "0.00",
            required = 0,
            languageIndependent=True,
            widget = atapi.DecimalWidget(
                label = _(u"label_price", default=u"Price"),
                description = _(u"desc_price", default=u""),
                size=8,
            ),
        ),

        ExtBooleanField('showPrice',
            default = False,
            languageIndependent=True,
            widget = atapi.BooleanWidget(
                label = _(u"label_show_price", default=u"Show price"),
                description = _(u"desc_show_price", default=u""),
            ),
        ),

        ExtStringField('skuCode',
            required = 0,
            languageIndependent=True,
            widget = atapi.StringWidget(
                label = _(u"label_sku_code", default=u"SKU code"),
                description = _(u"desc_sku_code", default=u""),
            ),
        ),

        ExtStringField('variation1_attribute',
            required = 0,
            widget = atapi.StringWidget(
                label = _(u"label_variation1_attr",
                          default=u"Variation 1 Attribute"),
                description = _(u"desc_variation1_attr", default=u""),
                visible={'view': 'invisible', 'edit': 'invisible'},
            ),
        ),

        ExtLinesField('variation1_values',
            required = 0,
            widget = atapi.LinesWidget(
                label = _(u"label_variation1_values",
                          default=u"Variation 1 Values"),
                description = _(u"desc_variation1_values", default=u""),
                visible={'view': 'invisible', 'edit': 'invisible'},
            ),
        ),


        ExtStringField('variation2_attribute',
            required = 0,
            widget = atapi.StringWidget(
                label = _(u"label_variation2_attr",
                          default=u"Variation 2 Attribute"),
                description = _(u"desc_variation2_attr", default=u""),
                visible={'view': 'invisible', 'edit': 'invisible'},
            ),
        ),


        ExtLinesField('variation2_values',
            required = 0,
            widget = atapi.LinesWidget(
                label = _(u"label_variation2_values",
                          default=u"Variation 2 Values"),
                description = _(u"desc_variation2_values", default=u""),
                visible={'view': 'invisible', 'edit': 'invisible'},
            ),
        ),

        ExtFixedPointField('vat',
            default = "0.0",
            required = 0,
            languageIndependent=True,
            widget = atapi.SelectionWidget(
                label = _(u"label_vat_rate", default=u"VAT rate"),
                description = _(u"desc_vat_rate", default=u"Please select the value-added tax rate for this item."),
                size=8,
                format='select',
            ),
            vocabulary_factory = 'ftw.shop.VATRatesVocabulary',
        ),


    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields
