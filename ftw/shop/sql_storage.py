from DateTime import DateTime

from zope.interface import implements
from z3c.saconfig import named_scoped_session
from ftw.shop.interfaces import IOrderStorage
from ftw.shop.model.order import Order
from ftw.shop.model.cartitems import CartItems

Session = named_scoped_session('ftw.shop')

class SQLOrderStorage(object):
    implements(IOrderStorage)
    
    def __init__(self):
        pass

    def getOrder(self, id):
        db_session = Session()
        return db_session.query(Order).filter_by(order_id=id).first()

    def getAllOrders(self):
        db_session = Session()
        return db_session.query(Order).all()

    def createOrder(self, status=None, date=None, customer_data=None, 
                    cart_data=None, total=None):
        db_session = Session()
        new_order = Order()
        new_order.status = status
        new_order.date = date
        new_order.total = total

        db_session.add(new_order)
        db_session.flush()
        order_id = new_order.order_id

        # calc order number
        now = DateTime()
        order_prefix = '%03d%s' % (now.dayOfYear() + 500, now.yy())
        order_number = '%s%04d' % (order_prefix, order_id)
        new_order.title = order_number

        for key in customer_data.keys():
            setattr(new_order, "customer_%s" % key, customer_data[key])

        # store cart in order
        for sku_code in cart_data.keys():
            cart_items = CartItems()
            db_session.add(cart_items)
            db_session.flush()
            cart_items.sku_code = sku_code
            cart_items.quantity = cart_data[sku_code]['quantity']
            cart_items.title = cart_data[sku_code]['title']
            cart_items.price = cart_data[sku_code]['price']
            cart_items.total = cart_data[sku_code]['total']
            cart_items.order_id = order_id
            cart_items.order = new_order
            db_session.flush()
            
        return order_id
        
    def flush(self):
        db_session = Session()
        db_session.flush()
