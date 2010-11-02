from datetime import datetime
from email.Utils import formataddr

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry
from zope.component import getUtility, getMultiAdapter

from ftw.shop.config import SESSION_ADDRESS_KEY, ONLINE_PENDING_KEY
from ftw.shop.exceptions import MissingCustomerInformation
from ftw.shop.exceptions import MissingOrderConfirmation
from ftw.shop.exceptions import MissingPaymentProcessor
from ftw.shop.interfaces import IMailHostAdapter
from ftw.shop.interfaces import IShopConfiguration
from ftw.shop.interfaces import IOrderStorage


class OrderManagerView(BrowserView):
    """Lists orders stored in a IOrderStorage
    """
    
    def __init__(self, context, request):
        registry = getUtility(IRegistry)
        self.shop_config = registry.forInterface(IShopConfiguration)
        self.order_storage_name = self.shop_config.order_storage
        super(OrderManagerView, self).__init__(context, request)

    __call__ = ViewPageTemplateFile('templates/order_manager.pt')

    def getOrders(self):
        order_storage = getUtility(IOrderStorage, 
                                   name=self.order_storage_name)
        orders = order_storage.getAllOrders()
        return orders

    def getOrder(self, order_id):
        order_storage = getUtility(IOrderStorage, 
                                   name=self.order_storage_name)
        order = order_storage.getOrder(order_id)
        return order
    
    def getOrderStorage(self):
        order_storage = getUtility(IOrderStorage, 
                                   name=self.order_storage_name)
        return order_storage

    def addOrder(self):
        """Add a new Order and return the order id.
        """

        session = self.context.REQUEST.SESSION

        # check for cart
        cart_view = getMultiAdapter((self, self.context.REQUEST),
                                    name=u'cart_view')
        cart_data = cart_view.cart_items()

        # check for customer data
        customer_data = session.get(SESSION_ADDRESS_KEY, {})
        if not customer_data:
            raise MissingCustomerInformation

        # check for order confirmation
        if not session.get('order_confirmation', None):
            raise MissingOrderConfirmation

        # check for payment processor
        if not session.get('payment_processor_choice', None):
            raise MissingPaymentProcessor

        # change security context to owner
        user = self.context.getWrappedOwner()
        newSecurityManager(self.context.REQUEST, user)

        order_storage = getUtility(IOrderStorage, 
                                   name=self.order_storage_name)
        order_id = order_storage.createOrder(status=ONLINE_PENDING_KEY,
                                             date=datetime.now(),
                                             customer_data=customer_data,
                                             total=cart_view.cart_total(),
                                             cart_data=cart_data)
        order_storage.flush()

        noSecurityManager()

        return order_id

    def sendOrderMail(self, order_id):
        """Send order confirmation mail of the order with the specified 
        order_id. Can be used if initial sending of order mail failed for 
        some reason.
        """

        order_storage = getUtility(IOrderStorage, 
                                   name=self.order_storage_name)
        order = order_storage.getOrder(order_id)

        fullname = "%s %s" % (order.customer_firstname,
                              order.customer_lastname)

        ltool = getToolByName(self.context, 'portal_languages')
        lang = ltool.getPreferredLanguage()

        registry = getUtility(IRegistry)
        shop_config = registry.forInterface(IShopConfiguration)

        # Send order confirmation mail to customer
        mailTo = formataddr((fullname, order.customer_email))

        if shop_config is not None:
            mailFrom = shop_config.shop_email
            mailBcc = getattr(shop_config, 'mail_bcc', '')
            shop_name = shop_config.shop_name
            mailSubject = getattr(shop_config, 'mail_subject_%s' % lang)
            if not mailSubject:
                mailSubject = '%s Webshop' % shop_name

        mhost = IMailHostAdapter(self.context)
        mail_view = getMultiAdapter((self.context, self.context.REQUEST),
                                    name=u'mail_view')
        msg_body = mail_view(order=order, 
                             shop_config=shop_config)

        mhost.send(msg_body,
                     mto=mailTo,
                     mfrom=mailFrom,
                     mbcc=mailBcc,
                     subject=mailSubject,
                     encode=None,
                     immediate=False,
                     msg_type='text/html',
                     charset='utf8')

        # Send mail to shop owner about the order
        mailTo = formataddr(("Shop Owner", shop_config.shop_email))

        if shop_config is not None:
            shop_name = shop_config.shop_name
            mailFrom = formataddr((shop_name, shop_config.shop_email))
            mailBcc = getattr(shop_config, 'mail_bcc', '')
            mailSubject = '[%s] Order %s by %s' % (shop_name,
                                                   order_id,
                                                   fullname)

        mhost = IMailHostAdapter(self.context)
        shopowner_mail_view = getMultiAdapter((self.context, self.context.REQUEST),
                                    name=u'shopowner_mail_view')
        msg_body = shopowner_mail_view(order=order,
                                       shop_config=shop_config)

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
