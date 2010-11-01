from decimal import Decimal, InvalidOperation

from sqlalchemy import Column, Integer, Unicode, Numeric
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from zope.interface import implements

from ftw.shop.interfaces import ICartItem
from ftw.shop.model.order import Order


Base = declarative_base()

def to_decimal(number):
    """Since SQLite doesn't support Decimal fields, trim the float it
    returns to two decimal places and convert it to Decimal. If that
    fails, return the total as-is."""
    try:
        return Decimal(str(number)[:str(number).find('.') + 3])
    except InvalidOperation:
        return number
    

class CartItems(Base):
    """Cart items model.
    This class represents one or more items with the same skuCode that are
    part of an order. An order therefore holds several of these CartItems
    objects, one for every unique item type.
    """

    implements(ICartItem)

    __tablename__ = 'cartitems'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey(Order.order_id))
    sku_code = Column(Unicode)
    quantity = Column(Integer)
    title = Column(Unicode)
    price = Column(Numeric)
    total = Column(Numeric)
    
    order = relationship(Order, backref=backref('cartitems', order_by=id))
    
    def getPrice(self):
        """Return the price converted to a Decimal
        """
        return to_decimal(self.price)
    
    def getTotal(self):
        """Return the total converted to a Decimal
        """
        return to_decimal(self.total)