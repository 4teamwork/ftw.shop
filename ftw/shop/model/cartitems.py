from decimal import Decimal, InvalidOperation

from sqlalchemy import Column, Integer, Unicode, Numeric
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from zope.interface import implements

from ftw.shop.interfaces import ICartItem
from ftw.shop.model.order import Order


Base = declarative_base()


class CartItems(Base):
    """Cart contents model
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
    
    def getTotal(self):
        """Since SQLite doesn't support Decimal fields, trim the float it
        returns to two decimal places and convert it to Decimal. If that
        fails, return the total as-is."""
        f = self.total
        try:
            return Decimal(str(f)[:str(f).find('.') + 3])
        except InvalidOperation:
            return self.total