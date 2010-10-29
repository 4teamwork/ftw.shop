from sqlalchemy import Column, Integer, Unicode
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
    
    order = relationship(Order, backref=backref('cartitems', order_by=id))