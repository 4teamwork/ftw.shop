import cStringIO
import csv
from datetime import datetime
from email.Utils import formataddr
from decimal import Decimal
from decimal import InvalidOperation

from Acquisition import aq_inner
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

from ftw.shop import shopMessageFactory as _
from ftw.shop.config import SESSION_ADDRESS_KEY
from ftw.shop.config import SESSION_SHIPPING_KEY
from ftw.shop.config import ONLINE_PENDING_KEY
from ftw.shop.exceptions import MissingCustomerInformation
from ftw.shop.exceptions import MissingShippingAddress
from ftw.shop.exceptions import MissingOrderConfirmation
from ftw.shop.exceptions import MissingPaymentProcessor
from ftw.shop.utils import UnicodeCSVWriter
from ftw.shop.interfaces import IMailHostAdapter
from ftw.shop.interfaces import IShopConfiguration
from ftw.shop.interfaces import IOrderStorage
from ftw.shop.interfaces import IPaymentProcessorStepGroup

DEBUG = True


class OrderManagerView(BrowserView):
    """Lists orders stored in a IOrderStorage
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.template = ViewPageTemplateFile('templates/order_manager.pt')
        self.request.set('disable_border', True)
        registry = getUtility(IRegistry)
        self.shop_config = registry.forInterface(IShopConfiguration)
        self.mhost = IMailHostAdapter(self.context)
        self.order_storage = getUtility(IOrderStorage,
                                        name=self.shop_config.order_storage)
        super(OrderManagerView, self).__init__(context, request)


    def __call__(self):
        self.from_date = self.request.get('from_date')
        self.to_date = self.request.get('to_date')
        self.order_results = self.getOrders(self.from_date, self.to_date)
        return self.template(self)


    def download_csv(self):
        """Returns a CSV file containing the shop orders
        """
        from Products.Archetypes.utils import contentDispositionHeader
        filename = "orders.csv"
        stream = cStringIO.StringIO()
        csv_writer = UnicodeCSVWriter(stream, delimiter=',',
                        quotechar='"', quoting=csv.QUOTE_MINIMAL)
        core_cols = ['order_id',
                      'title',
                      'status',
                      'total',
                      'date',
                      'customer_title',
                      'customer_firstname',
                      'customer_lastname',
                      'customer_email',
                      'customer_street1',
                      'customer_street2',
                      'customer_phone',
                      'customer_zipcode',
                      'customer_city',
                      'customer_shipping_address',
                      'customer_country',
                      'customer_newsletter',
                      'customer_comments']

        # Create union of core_cols + all_cols to retain order
        all_cols = self.order_storage.getFieldNames()
        columns = core_cols + filter(lambda x:x not in core_cols, all_cols)
        cart_cols = ['sku_code', 'quantity', 'title', 'price', 
                     'item_total', 'supplier_name', 'supplier_email']
        csv_writer.writerow(columns + cart_cols)

        self.from_date = self.request.get('from_date')
        self.to_date = self.request.get('to_date')
        for order in self.getOrders(self.from_date, self.to_date):
            order_data = [getattr(order, attr, '') for attr in columns]

            # Get the total via getTotal accessor to convert it to Decimal
            order_data[columns.index('total')] = order.getTotal()

            for cart_item in order.cartitems:
                cart_data = [cart_item.sku_code,
                            cart_item.quantity,
                            cart_item.title,
                            cart_item.getPrice(),
                            cart_item.getTotal(),
                            cart_item.supplier_name,
                            cart_item.supplier_email]

                csv_writer.writerow(order_data + cart_data)

        RESPONSE = self.request.RESPONSE
        header_value = contentDispositionHeader('attachment',
                                                'utf-8',
                                                filename=filename)
        if not DEBUG:
            RESPONSE.setHeader("Content-Disposition", header_value)
            RESPONSE.setHeader("Content-Type",
                               'text/comma-separated-values;charset=%s' % 'utf-8')
        stream.seek(0)
        return stream.read()

    def cancel_order(self):
        """Cancel an order by its order_id
        """
        context = aq_inner(self.context)
        ptool = getToolByName(context, 'plone_utils')
        order_id = self.request.get('order_id')
        cancel = self.request.get('cancel')
        if cancel:
            order_storage = self.getOrderStorage()
            order_storage.cancelOrder(order_id)
            ptool.addPortalMessage(
                _(u'msg_order_cancelled',
                  default=u"Order cancelled."),
                'info')
        self.request.response.redirect("%s/order_manager" % context.absolute_url())

    def getOrders(self, from_date=None, to_date=None):
        order_storage = self.order_storage
        all_orders = order_storage.getAllOrders()
        if from_date and to_date:
            from_date = from_date.asdatetime()
            to_date = to_date.asdatetime()
            orders = [o for o in all_orders if from_date.date() <= o.date.date() and to_date.date() >= o.date.date() ]
        else:
            orders = all_orders
        return orders

    def getOrder(self, order_id):
        order_storage = self.order_storage
        order = order_storage.getOrder(order_id)
        return order

    def getOrderStorage(self):
        return self.order_storage

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

        # check for shipping address
        shipping_data = session.get(SESSION_SHIPPING_KEY, {})
        if not shipping_data:
            raise MissingShippingAddress

        # check for order confirmation
        if not session.get('order_confirmation', None):
            raise MissingOrderConfirmation

        # check for payment processor
        payment_processor_step_groups = getAdapters(
                                        (self.context, self.request, self),
                                        IPaymentProcessorStepGroup)

        selected_pp_step_group = self.shop_config.payment_processor_step_group
        for name, step_group_adapter in payment_processor_step_groups:
            if name == selected_pp_step_group:
                payment_processor_steps = step_group_adapter.steps

        if not len(payment_processor_steps) == 0 \
            and not session.get('payment_processor_choice', None):
            raise MissingPaymentProcessor

        # change security context to owner
        user = self.context.getWrappedOwner()
        newSecurityManager(self.context.REQUEST, user)

        order_storage = self.order_storage
        order_id = order_storage.createOrder(status=ONLINE_PENDING_KEY,
                                             date=datetime.now(),
                                             customer_data=customer_data,
                                             shipping_data=shipping_data,
                                             total=cart_view.cart_total(),
                                             cart_data=cart_data)
        order_storage.flush()

        noSecurityManager()

        return order_id

    def sendOrderMails(self, order_id):
        """Send order confirmation and notification mails for the order with
        the specified order_id.
        """

        order = self.order_storage.getOrder(order_id)

        ltool = getToolByName(self.context, 'portal_languages')
        lang = ltool.getPreferredLanguage()

        # Send order confirmation to customer
        self._send_customer_mail(order, lang)

        # Send order notification to supplier(s)
        suppliers = []
        for item_type in order.cartitems:
            if not (item_type.supplier_name == '' \
                or item_type.supplier_email == ''):
                suppliers.append((item_type.supplier_name,
                                  item_type.supplier_email))
        unique_suppliers = set(suppliers)
        for supplier in unique_suppliers:
            self._send_supplier_mail(supplier, order)

        # Send order notification to shop owner
        self._send_owner_mail(order)

        return

    def _send_owner_mail(self, order):
        """Send order notification to shop owner.
        """
        all_prices_zero = self.all_prices_zero(order)
        mail_to = formataddr(("Shop Owner", self.shop_config.shop_email))
        customer_name = "%s %s" % (order.customer_firstname,
                                   order.customer_lastname)
        mail_subject = '[%s] Order %s by %s' % (self.shop_config.shop_name,
                                               order.order_id,
                                               customer_name)

        mail_view = getMultiAdapter((self.context, self.context.REQUEST),
                                    name=u'shopowner_mail_view')
        msg_body = mail_view(order=order,
                             all_prices_zero=all_prices_zero,
                             shop_config=self.shop_config)
        self._send_mail(mail_to, mail_subject, msg_body)

    def _send_customer_mail(self, order, lang):
        """Send order confirmation mail to customer
        """
        all_prices_zero = self.all_prices_zero(order)
        customer_name = "%s %s" % (order.customer_firstname,
                                   order.customer_lastname)
        mail_to = formataddr((customer_name, order.customer_email))

        mail_subject = getattr(self.shop_config, 'mail_subject_%s' % lang)
        if not mail_subject:
            mail_subject = '%s Webshop' % self.shop_config.shop_name

        mail_view = getMultiAdapter((self.context, self.context.REQUEST),
                                    name=u'mail_view')
        msg_body = mail_view(order=order,
                             all_prices_zero=all_prices_zero,
                             shop_config=self.shop_config)
        self._send_mail(mail_to, mail_subject, msg_body)

    def _send_supplier_mail(self, supplier, order):
        """Send order notification to a (single) supplier.
        """
        all_prices_zero = self.all_prices_zero(order)
        mail_to = formataddr(supplier)
        customer_name = "%s %s" % (order.customer_firstname,
                                   order.customer_lastname)
        mail_subject = '[%s] Order %s by %s' % (self.shop_config.shop_name,
                                               order.order_id,
                                               customer_name)

        mail_view = getMultiAdapter((self.context, self.context.REQUEST),
                                    name=u'supplier_mail_view')
        msg_body = mail_view(order=order,
                             all_prices_zero=all_prices_zero,
                             shop_config=self.shop_config)
        self._send_mail(mail_to, mail_subject, msg_body)

    def _send_mail(self, to, subject, body):
        """Send mail originating from the shop.
        """

        mail_bcc = getattr(self.shop_config, 'mail_bcc', '')
        mail_from = formataddr((self.shop_config.shop_name,
                               self.shop_config.shop_email))
        self.mhost.send(body,
             mto=to,
             mfrom=mail_from,
             mbcc=mail_bcc,
             subject=subject,
             encode=None,
             immediate=False,
             msg_type='text/html',
             charset='utf8')

    def all_prices_zero(self, order):
        try:
            prices = [item.price for item in order.cartitems]
            return all([p == Decimal('0.0') for p in prices])
        except InvalidOperation:
            return False


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
        order_view.order_id = int(id)
        order_view.__name__ = str(id)
        return order_view
