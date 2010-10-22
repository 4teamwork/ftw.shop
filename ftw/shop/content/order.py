from AccessControl import ClassSecurityInfo
from ftw.shop import shopMessageFactory as _
from ftw.shop.config import PROJECTNAME
from ftw.shop.interfaces import IShopOrder
from persistent.mapping import PersistentMapping
from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from zope.interface import implements
from zope.component import getUtility

from plone.registry.interfaces import IRegistry
from ftw.shop.interfaces import IShopConfiguration

OrderSchema = ATContentTypeSchema.copy() + atapi.Schema((

    atapi.FixedPointField(
        'total',
        required=False,
        widget=atapi.DecimalWidget(
            label=_(u'label_total', default=u"Total"),
            description=_(u"")
        ),
    ),
))


class ShopOrder(base.ATCTContent):
    """ A content type for storing shop orders.
    """
    implements(IShopOrder)
    security = ClassSecurityInfo()
    meta_type = 'ShopOrder' 
    schema = OrderSchema

    def setCustomerData(self, data):
        self._customer_data = PersistentMapping(data)

    def getCustomerData(self):
        if hasattr(self, '_customer_data'):
            return self._customer_data
        
    def getShopConfig(self):
        registry = getUtility(IRegistry)
        shop_config = registry.forInterface(IShopConfiguration)
        return shop_config

    def setCartData(self, data):
        self._cart_data = PersistentMapping(data)
        
    def getCartData(self):
        if hasattr(self, '_cart_data'):
            return self._cart_data
    
    def getOrderNumber(self):
        return self.Title() or self.getId()

atapi.registerType(ShopOrder, PROJECTNAME)
