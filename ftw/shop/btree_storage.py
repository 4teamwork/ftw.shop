from DateTime import DateTime
from decimal import Decimal

from AccessControl import ClassSecurityInfo
from persistent import Persistent
from Products.CMFCore.permissions import ModifyPortalContent
from zope.interface import implements

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


class Order(object):

    def __init__(self):
        self.order_id = None
        self.status = None
        self.date = None
        self.total = None
        self.title = None

        self.customer_title = None
        self.customer_firstname = None
        self.customer_lastname = None
        self.customer_email = None
        self.customer_street1 = None
        self.customer_street2 = None
        self.customer_phone = None
        self.customer_zipcode = None
        self.customer_city = None
        self.customer_country = None
        self.customer_shipping_address = None
        self.customer_newsletter = None
        self.customer_comments = None

        self.shipping_title = None
        self.shipping_firstname = None
        self.shipping_lastname = None
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


class CartItems(object):
    """Cart items model.
    """

    def __init__(self):
        self.id = None
        self.order_id = None
        self.sku_code = None
        self.quantity = None
        self.title = None
        self.price = None
        self.total = None
        self.supplier_name = None
        self.supplier_email = None

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
        for sku_code in cart_data.keys():
            cart_items = CartItems()
            cart_items.sku_code = sku_code
            cart_items.quantity = cart_data[sku_code]['quantity']
            cart_items.title = cart_data[sku_code]['title']
            cart_items.price = Decimal(cart_data[sku_code]['price'])
            cart_items.total = Decimal(cart_data[sku_code]['total'])
            cart_items.supplier_name = cart_data[sku_code]['supplier_name']
            cart_items.supplier_email = cart_data[sku_code]['supplier_email']
            cart_items.order_id = order_id
            cart_items.order = new_order
            all_cart_items.append(cart_items)

        new_order.cartitems = all_cart_items
        return order_id

    def flush(self):
        pass

    def getFieldNames(self):
        o = Order()
        field_names = [f for f in dir(o) if not (f.startswith('_') or \
                                                 f.startswith('get') or \
                                                 f == 'cartitems')]
        return field_names
