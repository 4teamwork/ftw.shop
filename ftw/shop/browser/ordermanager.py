from datetime import datetime
from email.Utils import formataddr

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry
from zope.publisher.interfaces.browser import IBrowserView
from zope.component import getUtility, getMultiAdapter, getAdapters
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


from ftw.shop.config import SESSION_ADDRESS_KEY, ONLINE_PENDING_KEY
from ftw.shop.exceptions import MissingCustomerInformation
from ftw.shop.exceptions import MissingOrderConfirmation
from ftw.shop.exceptions import MissingPaymentProcessor
from ftw.shop.interfaces import IMailHostAdapter
from ftw.shop.interfaces import IShopConfiguration
from ftw.shop.interfaces import IOrderStorage
from ftw.shop.interfaces import IPaymentProcessorStepGroup


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

        registry = getUtility(IRegistry)
        shop_config = registry.forInterface(IShopConfiguration)

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
        payment_processor_step_groups = getAdapters(
                                        (self.context, self.request, self),
                                        IPaymentProcessorStepGroup)
        
        selected_pp_step_group = shop_config.payment_processor_step_group
        for name, step_group_adapter in payment_processor_step_groups:
            if name == selected_pp_step_group:
                payment_processor_steps = step_group_adapter.steps
                
        if not len(payment_processor_steps) == 0 \
            and not session.get('payment_processor_choice', None):
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

        # Send mail to supplier(s) and shop owner about the order

        suppliers = []
        for item_type in order.cartitems:
            if not (item_type.supplier_name == '' \
                or item_type.supplier_email == ''):
                suppliers.append((item_type.supplier_name, item_type.supplier_email))
        unique_suppliers = set(suppliers)
        for supplier in unique_suppliers:
            self._send_supplier_mail(supplier, order)

#        mailTo = formataddr(("Shop Owner", shop_config.shop_email))
#
#        if shop_config is not None:
#            shop_name = shop_config.shop_name
#            mailFrom = formataddr((shop_name, shop_config.shop_email))
#            mailBcc = getattr(shop_config, 'mail_bcc', '')
#            mailSubject = '[%s] Order %s by %s' % (shop_name,
#                                                   order_id,
#                                                   fullname)

#        mhost = IMailHostAdapter(self.context)
#        shopowner_mail_view = getMultiAdapter((self.context, self.context.REQUEST),
#                                    name=u'shopowner_mail_view')
#        msg_body = shopowner_mail_view(order=order,
#                                       shop_config=shop_config)
#
#        mhost.send(msg_body,
#                     mto=mailTo,
#                     mfrom=mailFrom,
#                     mbcc=mailBcc,
#                     subject=mailSubject,
#                     encode=None,
#                     immediate=False,
#                     msg_type='text/html',
#                     charset='utf8')
        return

    def _send_supplier_mail(self, supplier, order):
        mailTo = formataddr(supplier)
        fullname = "%s %s" % (order.customer_firstname, order.customer_lastname)
        shop_name = self.shop_config.shop_name
        mailFrom = formataddr((shop_name, self.shop_config.shop_email))
        mailBcc = getattr(self.shop_config, 'mail_bcc', '')
        mailSubject = '[%s] Order %s by %s' % (shop_name,
                                               order.order_id,
                                               fullname)

        mhost = IMailHostAdapter(self.context)
        supplier_mail_view = getMultiAdapter((self.context, self.context.REQUEST),
                                    name=u'supplier_mail_view')
        msg_body = supplier_mail_view(order=order,
                                       shop_config=self.shop_config)

        mhost.send(msg_body,
                     mto=mailTo,
                     mfrom=mailFrom,
                     mbcc=mailBcc,
                     subject=mailSubject,
                     encode=None,
                     immediate=False,
                     msg_type='text/html',
                     charset='utf8')


class OrderView(BrowserView):
    """Lists a single order stored in a IOrderStorage
    """

    implements(IBrowserView, IPublishTraverse)

    __call__ = ViewPageTemplateFile('templates/order_view.pt')

    def __init__(self, context, request):
        registry = getUtility(IRegistry)
        self.shop_config = registry.forInterface(IShopConfiguration)
        self.order_storage_name = self.shop_config.order_storage
        super(OrderView, self).__init__(context, request)

    def getOrder(self, order_id=None):
        if not order_id:
            order_id = self.order_id
        order_storage = getUtility(IOrderStorage, 
                                   name=self.order_storage_name)
        order = order_storage.getOrder(order_id)
        return order

    def publishTraverse(self, request, id):
        """
        """
        order_view = OrderView(self.context, self.request)
        order_view.order_id = id
        order_view.__name__ = id
        return order_view
