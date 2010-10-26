from DateTime import DateTime as ZopeDateTime
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from sqlalchemy import Column, Integer, Unicode, Numeric, PickleType, DateTime
from sqlalchemy.ext.declarative import declarative_base

from ftw.shop.interfaces import IShopOrder
from zope.interface import implements
from ftw.shop.config import ONLINE_PENDING_KEY
from ftw.shop.interfaces import IShopConfiguration

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
    cart_contents = Column(PickleType)
    customer_info = Column(PickleType)
    date = Column(DateTime)


    def shop_config(self):
        registry = getUtility(IRegistry)
        shop_config = registry.forInterface(IShopConfiguration)
        return shop_config
    
    def getOrderNumber(self):
        order_id = self.order_id
        now = ZopeDateTime()
        order_number = '%03d%s%04d' % (now.dayOfYear()+500, now.yy(), order_id)
        return order_number

    def __repr__(self):
        return '<Order %s>' % self.order_id
