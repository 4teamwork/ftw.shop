from DateTime import DateTime
from decimal import Decimal

from AccessControl import ClassSecurityInfo
from persistent import Persistent
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

try:
    # Plone >= 4.0
    from zope.component.hooks import getSite

except ImportError:
    # Plone < 4.0
    from zope.app.component.hooks import getSite



from BTrees.IOBTree import IOBTree
try:
    from BTrees.LOBTree import LOBTree
    BTreeImplementation = LOBTree
except ImportError:
    BTreeImplementation = IOBTree
from BTrees.Length import Length

from ftw.shop.interfaces import IOrderStorage
from ftw.shop.utils import to_decimal


security = ClassSecurityInfo()


class Order(Persistent):

    def __init__(self):
        self.order_id = None
        self.status = None
        self.date = None
        self.total = None
        self.vat_amount = None
        self.title = None

        self.customer_title = None
        self.customer_firstname = None
        self.customer_lastname = None
        self.customer_email = None
        self.customer_company = None
        self.customer_street1 = None
        self.customer_street2 = None
        self.customer_phone = None
        self.customer_zipcode = None
        self.customer_city = None
        self.customer_country = None
        self.customer_shipping_address = None
        self.customer_comments = None

        self.shipping_title = None
        self.shipping_firstname = None
        self.shipping_lastname = None
        self.shipping_company = None
        self.shipping_street1 = None
        self.shipping_street2 = None
        self.shipping_zipcode = None
        self.shipping_city = None

        self.cartitems = None

    def getTotal(self):
        """Since SQLite doesn't support Decimal fields, trim the float it
        returns to two decimal places and convert it to Decimal. If that
        fails, return the total as-is."""
        return to_decimal(self.total)

    def getLocalizedDate(self):
        """Returns the localized order date and time.
        """
        site = getSite()
        util = getToolByName(site, 'translation_service')
        return util.ulocalized_time(self.date, long_format=True,
                                    context=site, domain='plonelocales')


class CartItems(Persistent):
    """Cart items model.
    """

    def __init__(self):
        self.id = None
        self.order_id = None
        self.sku_code = None
        self.quantity = None
        self.title = None
        self.price = None
        self.show_price = False
        self.total = None
        self.supplier_name = None
        self.supplier_email = None
        self.vat_rate = None
        self.vat_amount = None
        self.dimensions = None
        self.selectable_dimensions = None
        self.price_per_item = None

        self.order = None

    def getPrice(self):
        """Return the price converted to a Decimal
        """
        return to_decimal(self.price)

    def getTotal(self):
        """Return the total converted to a Decimal
        """
        return to_decimal(self.total)


class BTreeOrderStorage(Persistent):
    implements(IOrderStorage)
    title = u"BTree Storage"

    def __init__(self):
        self._orderStorage = BTreeImplementation()
        self._orderCount = 0
        self._length = Length()

    def getOrder(self, id):
        return self._orderStorage[id]

    def getAllOrders(self):
        return list(self._orderStorage.values())

    def _addDataRow(self, value):
        """Adds a row of data to the internal storage
        """

        # Get id for order to be added and increment internal counter
        id = self._orderCount + 1
        self._orderCount += 1

        self._orderStorage[id] = value
        self._length.change(1)
        return id


    security.declareProtected(ModifyPortalContent, 'createOrder')

    def createOrder(self, status=None, date=None, customer_data=None,
                    shipping_data=None, cart_data=None, total=None):
        """ a wrapper for the _addDataRow method """

        new_order = Order()
        new_order.status = status
        new_order.date = date
        new_order.total = Decimal(total)

        order_id = self._addDataRow(new_order)
        new_order.order_id = order_id

        # calc order number
        now = DateTime()
        order_prefix = '%03d%s' % (now.dayOfYear() + 500, now.yy())
        order_number = '%s%04d' % (order_prefix, order_id)
        new_order.title = order_number

        for key in customer_data.keys():
            setattr(new_order, "customer_%s" % key, customer_data[key])

        for key in shipping_data.keys():
            setattr(new_order, "shipping_%s" % key, shipping_data[key])

        # store cart in order
        all_cart_items = []
        vat_amount_total = Decimal('0.0')
        for key in cart_data.keys():
            cart_items = CartItems()
            cart_items.sku_code = cart_data[key]['skucode']
            cart_items.quantity = cart_data[key]['quantity']
            cart_items.title = cart_data[key]['title']
            cart_items.price = Decimal(cart_data[key]['price'])
            cart_items.show_price = cart_data[key]['show_price']
            cart_items.total = Decimal(cart_data[key]['total'])
            cart_items.supplier_name = cart_data[key]['supplier_name']
            cart_items.supplier_email = cart_data[key]['supplier_email']
            cart_items.vat_rate = cart_data[key]['vat_rate']
            cart_items.vat_amount = Decimal(cart_data[key]['vat_amount'])
            cart_items.dimensions = cart_data[key]['dimensions']
            cart_items.selectable_dimensions = cart_data[key]['selectable_dimensions']
            cart_items.price_per_item = cart_data[key]['price_per_item']
            cart_items.order_id = order_id
            cart_items.order = new_order

            all_cart_items.append(cart_items)
            vat_amount_total += cart_items.vat_amount

        new_order.cartitems = all_cart_items
        new_order.vat_amount = vat_amount_total
        return order_id

    def cancelOrder(self, order_id):
        del self._orderStorage[order_id]
        self._length.change(-1)

    def flush(self):
        pass

    def getFieldNames(self):
        o = Order()
        field_names = [f for f in dir(o) if not (f.startswith('_') or \
                                                 f.startswith('get') or \
                                                 f == 'cartitems')]
        return field_names
