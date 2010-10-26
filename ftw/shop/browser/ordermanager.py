import logging
from DateTime import DateTime
from email import message_from_string
from email.Header import Header
from email.Utils import formataddr

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
from plone.memoize import instance
from Acquisition import aq_inner
from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
import transaction
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

from ftw.shop.config import CATEGORY_RELATIONSHIP
from ftw.shop.interfaces import IVariationConfig
from ftw.shop.utils import create_session
from ftw.shop.model.order import Order
from ftw.shop.config import PROJECTNAME
from ftw.shop.config import SESSION_ADDRESS_KEY, SESSION_ORDERS_KEY
from ftw.shop.exceptions import MissingCustomerInformation, MissingOrderConfirmation
from ftw.shop.interfaces import IMailHostAdapter
from ftw.shop.interfaces import IShopConfiguration


class OrderManagerView(BrowserView):
    """Lists orders stored with SQLAlchemy
    """

    __call__ = ViewPageTemplateFile('templates/order_manager.pt')
    
    def getOrders(self):
        sa_session = create_session()
        orders = sa_session.query(Order)
        return orders

    def addOrder(self):
        '''
        Add a new Order and returns the order id.
        '''

        session = self.context.REQUEST.SESSION

        # check for cart
        cart_view = getMultiAdapter((self, self.context.REQUEST), name=u'cart_view')
        cart_data = cart_view.cart_items()
       
        # check for customer data
        customer_data = session.get(SESSION_ADDRESS_KEY, {})
        if not customer_data:
            raise MissingCustomerInformation
        
        # check for order confirmation
        if not session.get('order_confirmation', None):
            raise MissingOrderConfirmation
        
        # change security context to owner
        user = self.context.getWrappedOwner()
        newSecurityManager(self.context.REQUEST, user)
        
        # create Order
        sa_session = create_session()
        order = Order()
        sa_session.add(order)
        transaction.commit()
        
        order_id = order.order_id

        # calc order number
        now  = DateTime()
        order_number = '%03d%s%04d' % (now.dayOfYear()+500, now.yy(), order_id )
        order.title = order_number
 
        # store customer data
        order.customer_info = customer_data

        # store cart in order
        order.cart_contents = cart_data
        order.total = cart_view.cart_total()
        
        sa_session.add(order)
        transaction.commit()

        noSecurityManager()

        return order_id


    def sendOrderMail(self, order_id):
        """
        Send order confirmation mail of the order with the specified order_id.
        Can be used if initial sending of order mail failed for some reason.
        """
        sa_session = create_session()
        order = sa_session.query(Order).filter_by(order_id=order_id).first()
        
        customer = order.customer_info
        
        fullname = "%s %s" % (customer.get('firstname'),customer.get('lastname'))

        ltool = getToolByName(self, 'portal_languages')
        lang = ltool.getPreferredLanguage()

        registry = getUtility(IRegistry)
        shop_config = registry.forInterface(IShopConfiguration)

        mailTo = formataddr((fullname, customer.get('email')))

        if shop_config is not None:
            mailFrom = shop_config.shop_email
            mailBcc = getattr(shop_config, 'mail_bcc', '')
            shop_name = shop_config.shop_name
            mailSubject = getattr(shop_config, 'mail_subject_%s' % lang)
            if not mailSubject:
                mailSubject = '%s Webshop' % shop_name

        mhost = IMailHostAdapter(self.context)
        mail_view = getMultiAdapter((order, self.context.REQUEST), name=u'mail_view')
        msg_body = mail_view()

        mhost.send(msg_body,
                     mto=mailTo,
                     mfrom=mailFrom,
                     mbcc=mailBcc,
                     subject=mailSubject,
                     encode=None,
                     immediate=False,
                     msg_type='text/html',
                     charset='utf8')
        return
