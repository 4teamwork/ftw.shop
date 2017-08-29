# -*- coding: utf-8 -*-
"""Definition of the Shop Item content type
"""

from Acquisition import aq_parent
from Products.Archetypes import atapi
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.configuration import zconf
from Products.Archetypes.public import AnnotationStorage

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

from ftw.shop.interfaces import IBuyable
from ftw.shop.interfaces import IShopItem
from ftw.shop.interfaces import IVariationConfig
from ftw.shop.content.categorizeable import Categorizeable
from ftw.shop.config import PROJECTNAME
from ftw.shop import shopMessageFactory as _


selectable_dimensions = {
    'no_dimensions': {
        'label': _(u"label_no_dimensions", default=u"---"),
        'dimension_unit': None,
        'dimensions': []
    },
    'length_mm_mm': {
        'label': _(u"label_length", default=u"Length"),
        'dimension_unit': u'mm',
        'dimensions': [_(u"Length (mm)")]
    },
    'length_m_m': {
        'label': _(u"label_length", default=u"Length"),
        'dimension_unit': u'm',
        'dimensions': [_(u"Length (m)")]
    },
    'length_width_mm_mm2': {
        'label': _(u"label_l_w", default=u"Length, Width"),
        'dimension_unit': u'mm²',
        'dimensions': [
            _(u"Length (mm)"),
            _(u"Width (mm)")]
    },
    'length_width_mm_m2': {
        'label': _(u"label_l_w", default=u"Length, Width"),
        'price_unit': u'm²',
        'price_to_dimension_modifier': 1000000,
        'dimension_unit': u'mm²',
        'dimensions': [
            _(u"Length (mm)"),
            _(u"Width (mm)")]
    },
    'length_width_thickness_mm_mm3': {
        'label': _(u"label_l_w_t", default=u"Length, Width, Thickness"),
        'dimension_unit': u'mm³',
        'dimensions': [
            _(u"Length (mm)"),
            _(u"Width (mm)"),
            _(u"Thickness (mm)")]
    },
    'length_width_thickness_mm_m3': {
        'label': _(u"label_l_w_t", default=u"Length, Width, Thickness"),
        'price_unit': u'm³',
        'price_to_dimension_modifier': 1000000000,
        'dimension_unit': u'mm³',
        'dimensions': [
            _(u"Length (mm)"),
            _(u"Width (mm)"),
            _(u"Thickness (mm)")]
    },
    'weight_g_g': {
        'label': _(u'label_weight', default=u"Weight"),
        'dimension_unit': u'g',
        'dimensions': [_(u"Weight (g)")]
    },
    'weight_g_kg': {
        'label': _(u'label_weight', default=u"Weight"),
        'price_unit': u'kg',
        'price_to_dimension_modifier': 1000,
        'dimension_unit': u'g',
        'dimensions': [_(u"Weight (g)")]
    },
    'weight_kg_kg': {
        'label': _(u'label_weight', default=u"Weight"),
        'dimension_unit': u'kg',
        'dimensions': [_(u"Weight (kg)")]
    }
}

ShopItemSchema = ATContentTypeSchema.copy() + atapi.Schema((

        atapi.ImageField(
            'image',
            required=False,
            languageIndependent=True,
            widget = atapi.ImageWidget(
                label = _(u"label_image", default=u"Image"),
            ),
            storage=AnnotationStorage(),
                sizes= {'large': (768, 768),
                         'mini': (200, 200),
                         'thumb': (128, 128),
                  },
            ),


        atapi.TextField(
            'text',
            required=False,
            searchable=True,
            primary=True,
            storage=atapi.AnnotationStorage(migrate=True),
            allowable_content_types=('text/html', ),
            default_content_type='text/html',
            validators=('isTidyHtmlWithCleanup', ),
            default_input_type='text/html',
            default_output_type='text/x-html-safe',
            widget=atapi.RichWidget(
                description='',
                label=_(u'label_body_text', default=u'Body Text'),
                rows=25,
                allow_file_upload = zconf.ATDocument.allow_document_upload),
            ),
        atapi.FixedPointField(
            'price',
            default = "0.00",
            required = 0,
            languageIndependent=True,
            widget = atapi.DecimalWidget(
                label = _(u"label_price", default=u"Price"),
                description = _(u"desc_price", default=u""),
                size=8,
                ),
            ),

        atapi.BooleanField(
            'showPrice',
            default = False,
            languageIndependent=True,
            widget = atapi.BooleanWidget(
                label = _(u"label_show_price", default=u"Show price"),
                description = _(u"desc_show_price", default=u""),
                ),
            ),

        atapi.StringField(
            'skuCode',
            required = 0,
            languageIndependent=True,
            widget = atapi.StringWidget(
                label = _(u"label_sku_code", default=u"SKU code"),
                description = _(u"desc_sku_code", default=u""),
                ),
            ),

        atapi.TextField(
            name='unit',
            searchable=True,
            widget=atapi.StringWidget(
                label=_(u'label_unit', default='Unit'),
                description=_(
                    u'description_unit',
                    default='The unit for the product quantity.'),
            ),
            schemata='default',
        ),

        atapi.StringField(
            'selectable_dimensions',
            required=True,
            vocabulary_factory='ftw.shop.selectable_dimensions_vocabulary',
            widget=atapi.SelectionWidget(
                format='select',
                label=_(u'label_selectable_dimensions',
                        default=u'Selectable dimensions'),
                description=_(
                    u'description_dimensions',
                    default='Specifies which dimensions of the product can '
                            'be chosen by the user. The price is per base unit '
                            '(mm, g, etc.).')
            ),
            schemata='default'
        ),

        atapi.StringField(
            'variation1_attribute',
            required = 0,
            widget = atapi.StringWidget(
                label = _(u"label_variation1_attr",
                          default=u"Variation 1 Attribute"),
                description = _(u"desc_variation1_attr", default=u""),
                visible={'view': 'invisible', 'edit': 'invisible'},
                ),
            ),

        atapi.LinesField(
            'variation1_values',
            required = 0,
            widget = atapi.LinesWidget(
                label = _(u"label_variation1_values",
                          default=u"Variation 1 Values"),
                description = _(u"desc_variation1_values", default=u""),
                visible={'view': 'invisible', 'edit': 'invisible'},
                ),
            ),


        atapi.StringField(
            'variation2_attribute',
            required = 0,
            widget = atapi.StringWidget(
                label = _(u"label_variation2_attr",
                          default=u"Variation 2 Attribute"),
                description = _(u"desc_variation2_attr", default=u""),
                visible={'view': 'invisible', 'edit': 'invisible'},
                ),
            ),

        atapi.LinesField(
            'variation2_values',
            required = 0,
            widget = atapi.LinesWidget(
                label = _(u"label_variation2_values",
                          default=u"Variation 2 Values"),
                description = _(u"desc_variation2_values", default=u""),
                visible={'view': 'invisible', 'edit': 'invisible'},
                ),
            ),

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


class ShopItem(Categorizeable, ATCTContent):
    """A simple shop item"""
    implements(IShopItem)
    alsoProvides(IBuyable)

    meta_type = "ShopItem"
    schema = ShopItemSchema

    def SearchableText(self):
        """ Make variations searchable. """
        data = super(ShopItem, self).SearchableText()

        var_conf = IVariationConfig(self)
        variation_details = []
        if var_conf.hasVariations():
            for variation in var_conf.getVariationDict().values():
                if not variation['active']:
                    continue
                variation_details.append(variation['description'])
                variation_details.append(variation['skuCode'])

        return ' '.join([
            data,
            ' '.join(self.getVariation1_values()),
            ' '.join(self.getVariation2_values()),
            ' '.join(variation_details),
            self.getSkuCode()
        ])

    def getDimensionDict(self):
        dim_key = self.Schema().getField('selectable_dimensions').get(self)
        if not dim_key or dim_key not in selectable_dimensions:
            return selectable_dimensions['no_dimensions']

        return selectable_dimensions[dim_key]

    def getSelectableDimensions(self):
        dimension_dict = self.getDimensionDict()
        return dimension_dict.get('dimensions', [])

    def getDimensionsLabel(self):
        dimension_dict = self.getDimensionDict()
        return dimension_dict.get('dimension_unit', None)

    def getPriceUnit(self):
        dimension_dict = self.getDimensionDict()
        if 'price_unit' in dimension_dict:
            return dimension_dict['price_unit']
        return dimension_dict.get('dimension_unit', None)

    def getPriceModifier(self):
        dimension_dict = self.getDimensionDict()
        return dimension_dict.get('price_to_dimension_modifier', 1)


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
