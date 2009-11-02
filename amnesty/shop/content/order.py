
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi

from Products.ATContentTypes.content import base
from Products.ATContentTypes.content.schemata import ATContentTypeSchema

from amnesty.shop.config import PROJECTNAME
#from Products.AIWebShop.Currency import Currency
from persistent.mapping import PersistentMapping
from amnesty.shop import shopMessageFactory as _

OrderSchema = ATContentTypeSchema.copy() + atapi.Schema((

    atapi.FloatField(
        'total',
        required=False,
        widget=atapi.DecimalWidget(
            label=_(u"Total"),
            description=_(u"")
        ),
    ),
))


class ShopOrder(base.ATCTContent):
    """ A shop order
    """
    security = ClassSecurityInfo()
    meta_type = 'ShopOrder' 
    schema = OrderSchema


    def setCustomerData(self, data):
        self._customer_data = PersistentMapping(data)

    def getCustomerData(self):
        if hasattr(self, '_customer_data'):
           return self._customer_data

    def setCartData(self, data):
        self._cart_data = PersistentMapping(data)
        
    def getCartData(self):
        if hasattr(self, '_cart_data'):
            return self._cart_data
    
    security.declarePublic('getOrderId')
    def getOrderId(self):
        """
        
        """
        
        return self.getId()

    def getOrderNumber(self):
        return self.Title() or self.getId()
    

    




atapi.registerType(ShopOrder, PROJECTNAME)


