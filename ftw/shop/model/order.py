from DateTime import DateTime as ZopeDateTime
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from sqlalchemy import Column, Integer, Unicode, Numeric, PickleType, DateTime
from sqlalchemy import Boolean
from sqlalchemy.ext.declarative import declarative_base

from ftw.shop.interfaces import IShopOrder
from zope.interface import implements
from ftw.shop.config import ONLINE_PENDING_KEY
from ftw.shop.interfaces import IShopConfiguration
from decimal import Decimal, InvalidOperation

Base = declarative_base()

class Order(Base):
    """Order model
    """

    implements(IShopOrder)

    __tablename__ = 'orders'

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Unicode)
    status = Column(Integer, default=ONLINE_PENDING_KEY)
    total = Column(Numeric)
    date = Column(DateTime)

    cart_contents = Column(PickleType)
    customer_info = Column(PickleType)

    customer_title = Column(Unicode)
    customer_firstname = Column(Unicode)
    customer_lastname = Column(Unicode)
    customer_email = Column(Unicode)
    customer_street1 = Column(Unicode)
    customer_street2 = Column(Unicode)
    customer_phone = Column(Unicode)
    customer_zipcode = Column(Unicode)
    customer_city = Column(Unicode)
    customer_country = Column(Unicode)
    customer_newsletter = Column(Boolean)
    customer_comments = Column(Unicode)


    def shop_config(self):
        registry = getUtility(IRegistry)
        shop_config = registry.forInterface(IShopConfiguration)
        return shop_config
    
    def getOrderNumber(self):
        order_id = self.order_id
        now = ZopeDateTime()
        order_number = '%03d%s%04d' % (now.dayOfYear()+500, now.yy(), order_id)
        return order_number
    
    def getTotal(self):
        """Since SQLite doesn't support Decimal fields, trim the float it
        returns to two decimal places and convert it to Decimal. If that
        fails, return the total as-is."""
        f = self.total
        try:
            return Decimal(str(f)[:str(f).find('.') + 3])
        except InvalidOperation:
            return self.total

    def __repr__(self):
        return '<Order %s>' % self.order_id
