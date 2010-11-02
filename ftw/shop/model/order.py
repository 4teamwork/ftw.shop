from decimal import Decimal, InvalidOperation
from DateTime import DateTime as ZopeDateTime

from plone.registry.interfaces import IRegistry
from sqlalchemy import Column, Integer, Unicode, Numeric, DateTime
from sqlalchemy import Boolean
from sqlalchemy.ext.declarative import declarative_base
from zope.interface import implements
from zope.component import getUtility

from ftw.shop.interfaces import IShopOrder
from ftw.shop.interfaces import IShopConfiguration
from ftw.shop.config import ONLINE_PENDING_KEY
from ftw.shop.utils import to_decimal


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


    def getTotal(self):
        """Since SQLite doesn't support Decimal fields, trim the float it
        returns to two decimal places and convert it to Decimal. If that
        fails, return the total as-is."""
        return to_decimal(self.total)

    def __repr__(self):
        return '<Order %s>' % self.order_id
