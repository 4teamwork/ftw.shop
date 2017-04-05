# -*- coding: utf-8 -*-
import cStringIO
import csv
from datetime import datetime
from datetime import date
from email.Utils import formataddr

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from Acquisition import aq_inner
from plone.registry.interfaces import IRegistry
from Products.Archetypes.utils import contentDispositionHeader
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getAdapter
from zope.component import getAdapters
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserView
from zope.i18n import translate

from ftw.shop import shopMessageFactory as _
from ftw.shop.config import ONLINE_PENDING_KEY
from ftw.shop.config import SESSION_ADDRESS_KEY
from ftw.shop.config import SESSION_REVIEW_KEY
from ftw.shop.config import SESSION_SHIPPING_KEY
from ftw.shop.exceptions import MissingCustomerInformation
from ftw.shop.exceptions import MissingOrderConfirmation
from ftw.shop.exceptions import MissingPaymentProcessor
from ftw.shop.exceptions import MissingShippingAddress
from ftw.shop.interfaces import IMailHostAdapter
from ftw.shop.interfaces import IOrderStorage
from ftw.shop.interfaces import IPaymentProcessorStepGroup
from ftw.shop.interfaces import IShopConfiguration

try:
    # Python > 2.5
    strptime = datetime.strptime
except AttributeError:
    # Python 2.4
    import time
    def strptime(date_string, format):
        return datetime(*(time.strptime(date_string, format)[0:6]))

try:
    dummy = type(any)
except NameError:
    # Python 2.4
    def any(iterable):
        for element in iterable:
            if element:
                return True
        return False



DEBUG = False

COLUMN_TITLES = {
    'order_id': 'Bestellungs-ID',
    'title': 'Bestellnummer',
    'status': 'Status',
    'total': 'Total',
    'date': 'Datum',
    'customer_attn': 'Zu Handen von',
    'customer_title': 'Anrede',
    'customer_firstname': 'Vorname',
    'customer_lastname': 'Nachname',
    'customer_company': 'Firma',
    'customer_department_code': 'Postkürzel',
    'customer_cost_center': 'Kostenstelle',
    'customer_email': 'e-Mail',
    'customer_street1': 'Strasse',
    'customer_street2': 'Adresszusatz',
    'customer_phone': 'Telefon',
    'customer_zipcode': 'PLZ',
    'customer_city': 'Ort',
    'customer_shipping_address': 'Bestelladresse',
    'customer_country': 'Land',
    'customer_comments': 'Kommentare',

    'shipping_title': 'Lieferadresse Anrede',
    'shipping_firstname': 'Lieferadresse Vorname',
    'shipping_lastname': 'Lieferadresse Nachname',
    'shipping_company': 'Lieferadresse Firma',
    'shipping_department_code': 'Lieferadresse Postkürzel',
    'shipping_street1': 'Lieferadresse Strasse',
    'shipping_street2': 'Lieferadresse Adresszusatz',
    'shipping_zipcode': 'Lieferadresse PLZ',
    'shipping_city': 'Lieferadresse Ort',

    'sku_code': 'Artikel-Nr',
    'quantity': 'Menge',
    'dimensions': 'Abmessung',
    'title': 'Titel',
    'price': 'Preis',
    'show_price': 'Preis anzeigen',
    'item_total': 'Subtotal',
    'supplier_name': 'Lieferant',
    'supplier_email': 'Lieferant e-Mail',
    'vat_amount': 'MwSt',
}


class OrderManagerView(BrowserView):
    """Lists orders stored in a IOrderStorage
    """

    template = ViewPageTemplateFile('templates/order_manager.pt')
    change_status_tmpl = ViewPageTemplateFile('templates/status.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.request.set('disable_border', True)
        registry = getUtility(IRegistry)
        self.shop_config = registry.forInterface(IShopConfiguration)
        self.mhost = IMailHostAdapter(self.context)
        self.order_storage = getUtility(IOrderStorage,
                                        name=self.shop_config.order_storage)
        self.supplier_filter = None
        self.status_filter = None
        super(OrderManagerView, self).__init__(context, request)


    def __call__(self):
        from_date, to_date = self.parse_date_range()
        self.supplier_filter = self.request.form.get('supplier',
            'all_suppliers')
        self.status_filter = self.request.form.get('form.widgets.status_filter', 'all')
        self.order_results = self.getOrders(from_date, to_date)
        if self.request.form.get('filter'):
            return self.__of__(self.context).template()
        elif self.request.form.get('download_csv'):
            return self.download_csv()
        elif self.request.form.get('cancel_orders'):
            return self.cancel_orders()
        elif self.request.form.get('change_status_step1'):
            return self.__of__(self.context).change_status_tmpl()
        elif self.request.form.get('change_status'):
            return self.change_status()
        else:
            return self.__of__(self.context).template()


    def parse_date_range(self):
        """Parse the from_date and to_date strings,
        assuming the jQuery UI datepicker widget always
        stores them in the request in the "%d.%m.%Y"
        format.
        """

        try:
            from_date = strptime(self.request.form.get(
                'from_date', ''), "%d.%m.%Y").date()
        except ValueError:
            from_date = date(2001, 1, 1)
        try:
            to_date = strptime(self.request.form.get(
                'to_date', ''), "%d.%m.%Y").date()
        except ValueError:
            to_date = date(2100, 1, 1)
        return (from_date, to_date)


    def getSuppliers(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(portal_type="Supplier")
        results = [dict(name=b.Title, email=b.email) for b in brains]
        return results

    def download_csv(self):
        """Returns a CSV file containing the shop orders
        """

        filename = "orders.csv"
        stream = cStringIO.StringIO()
        csv_writer = csv.writer(stream, dialect='excel', delimiter=';',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        core_cols = ['order_id',
                      'title',
                      'status',
                      'total',
                      'date',
                      'customer_title',
                      'customer_firstname',
                      'customer_lastname',
                      'customer_company',
                      'customer_email',
                      'customer_street1',
                      'customer_street2',
                      'customer_phone',
                      'customer_zipcode',
                      'customer_city',
                      'customer_shipping_address',
                      'customer_country',
                      'customer_comments']

        # Create union of core_cols + all_cols to retain order
        all_cols = self.order_storage.getFieldNames()
        columns = core_cols + filter(lambda x:x not in core_cols, all_cols)
        cart_cols = ['sku_code', 'quantity', 'dimensions', 'title', 'price',
                     'item_total', 'supplier_name', 'supplier_email']

        column_titles = [COLUMN_TITLES[col].decode('utf-8').encode('cp1252') for col in columns + cart_cols]
        # Write header row
        csv_writer.writerow(column_titles)

        for order in self.order_results:
            order_data = [getattr(order, attr, '') for attr in columns]

            # Get the total via getTotal accessor to convert it to Decimal
            order_data[columns.index('total')] = order.getTotal()

            for i, value in enumerate(order_data):
                if isinstance(value, unicode):
                    order_data[i] = value.encode('cp1252')

            for cart_item in order.cartitems:
                # format dimensions
                dimensions = [(cart_item.dimensions[i], dim) for i, dim in enumerate(cart_item.selectable_dimensions)]
                dim_strings = [' '.join([str(dim[0]), translate(_(dim[1]), context=self.request)]) for dim in dimensions]
                dim_formatted = ','.join(dim_strings)

                cart_data = [cart_item.sku_code,
                            cart_item.quantity,
                            dim_formatted,
                            cart_item.title,
                            cart_item.getPrice(),
                            cart_item.getTotal(),
                            cart_item.supplier_name,
                            cart_item.supplier_email]

                for i, value in enumerate(cart_data):
                    if isinstance(value, unicode):
                        cart_data[i] = value.encode('cp1252')

                csv_writer.writerow(order_data + cart_data)

        RESPONSE = self.request.RESPONSE
        header_value = contentDispositionHeader('attachment',
                                                'cp1252',
                                                filename=filename)
        if not DEBUG:
            RESPONSE.setHeader("Content-Disposition", header_value)
            RESPONSE.setHeader("Content-Type",
                           'text/comma-separated-values;charset=%s' % 'cp1252')
        else:
            RESPONSE.setHeader("Content-Type",
                           'text/plain; charset=%s' % 'cp1252')

        stream.seek(0)
        return stream.read()

    def cancel_orders(self):
        """Cancel orders by their order_ids
        """
        context = aq_inner(self.context)
        ptool = getToolByName(context, 'plone_utils')
        order_storage = self.getOrderStorage()

        orders = self.request.form.get('orders', [])
        for order_id in orders:
            try:
                order_id = int(order_id)
            except ValueError:
                # Invalid order_id - continue with next one
                continue
            order_storage.cancelOrder(order_id)
        msg = _(u'msg_order_cancelled',
                default=u"${no_orders} orders cancelled.",
                mapping={ u"no_orders" : len(orders)})
        ptool.addPortalMessage(msg, 'info')
        self.request.response.redirect("%s/order_manager" % context.absolute_url())

    def change_status(self):
        """Change status of several orders at once
        """
        context = aq_inner(self.context)
        ptool = getToolByName(context, 'plone_utils')
        order_storage = self.getOrderStorage()

        orders = self.request.form.get('orders', [])
        new_status = self.request.form.get('form.widgets.status', None)

        # Change status of the orders
        for order_id in orders:
            try:
                order_id = int(order_id)
            except ValueError:
                # Invalid order_id - continue with next one
                continue
            order = order_storage.getOrder(order_id)
            order.status = int(new_status)

        msg = _(u'msg_status_changed',
                default=u"Changed status for ${no_orders} orders.",
                mapping={ u"no_orders" : len(orders)})
        ptool.addPortalMessage(msg, 'info')
        return self.template()


    def getOrders(self, from_date=None, to_date=None):
        order_storage = self.order_storage
        all_orders = order_storage.getAllOrders()

        if any([from_date and to_date, self.supplier_filter, self.status_filter]):
            # Filter orders
            orders = []
            for order in all_orders:
                suppliers = [item.supplier_name for item in order.cartitems]
                if (self.supplier_filter in suppliers
                or self.supplier_filter in ["all_suppliers", "", None]) \
                and self.status_filter == str(order.status) \
                or self.status_filter == "all" \
                and from_date <= order.date.date() \
                and to_date >= order.date.date():
                    orders.append(order)
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
        cart_view = getMultiAdapter((self.context, self.context.REQUEST),
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

        # check for review data
        review_data = session.get(SESSION_REVIEW_KEY, {})
        # The comment was previously in the customer data step. If we move it
        # to the customer data set we can avoid changing all templates.
        customer_data.update(review_data)

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
                for email_address in item_type.supplier_email.split(','):
                    suppliers.append((item_type.supplier_name,
                                      email_address.strip()))
        unique_suppliers = set(suppliers)
        for supplier in unique_suppliers:
            self._send_supplier_mail(supplier, order)

        # Send order notification to shop owner
        if self.shop_config.always_notify_shop_owner:
            self._send_owner_mail(order)

        return

    def _send_owner_mail(self, order):
        """Send order notification to shop owner.
        """
        show_prices = self.show_prices(order)
        mail_to = formataddr(("Shop Owner", self.shop_config.shop_email))
        customer_name = "%s %s" % (order.customer_firstname,
                                   order.customer_lastname)
        customer_address = formataddr((customer_name, order.customer_email))
        mail_subject = '[%s] Order %s by %s' % (self.shop_config.shop_name,
                                               order.order_id,
                                               customer_name)

        mail_view = getMultiAdapter((self.context, self.context.REQUEST),
                                    name=u'shopowner_mail_view')
        msg_body = mail_view(order=order,
                             show_prices=show_prices,
                             has_order_dimensions=self.has_order_dimensions(order),
                             shop_config=self.shop_config)
        self._send_mail(mail_to, mail_subject, msg_body, reply_to=customer_address)

    def _send_customer_mail(self, order, lang):
        """Send order confirmation mail to customer
        """
        show_prices = self.show_prices(order)
        customer_name = "%s %s" % (order.customer_firstname,
                                   order.customer_lastname)
        mail_to = formataddr((customer_name, order.customer_email))

        mail_subject = self.shop_config.mail_subject
        if not mail_subject:
            mail_subject = u'Your Webshop Order'
        mail_subject = translate(mail_subject, domain='ftw.shop',
                                 context=self.request, default=mail_subject)

        mail_view = getMultiAdapter((self.context, self.context.REQUEST),
                                    name=u'mail_view')
        msg_body = mail_view(order=order,
                             show_prices=show_prices,
                             has_order_dimensions=self.has_order_dimensions(order),
                             shop_config=self.shop_config)
        self._send_mail(mail_to, mail_subject, msg_body)

    def _send_supplier_mail(self, supplier, order):
        """Send order notification to a (single) supplier.
        """
        show_prices = self.show_prices(order)
        mail_to = formataddr(supplier)
        customer_name = "%s %s" % (order.customer_firstname,
                                   order.customer_lastname)
        customer_address = formataddr((customer_name, order.customer_email))
        mail_subject = '[%s] Order %s by %s' % (self.shop_config.shop_name,
                                               order.order_id,
                                               customer_name)

        mail_view = getMultiAdapter((self.context, self.context.REQUEST),
                                    name=u'supplier_mail_view')
        msg_body = mail_view(order=order,
                             show_prices=show_prices,
                             has_order_dimensions=self.has_order_dimensions(order),
                             shop_config=self.shop_config,
                             supplier=supplier)
        self._send_mail(mail_to, mail_subject, msg_body, reply_to=customer_address)

    def _send_mail(self, to, subject, body, reply_to=None):
        """Send mail originating from the shop.
        """

        mail_bcc = getattr(self.shop_config, 'mail_bcc', '')
        mail_from = formataddr((self.shop_config.shop_name,
                               self.shop_config.shop_email))
        self.mhost.send(body,
             mto=to,
             mfrom=mail_from,
             mbcc=mail_bcc,
             reply_to=reply_to,
             subject=subject,
             encode=None,
             immediate=False,
             msg_type='text/html',
             charset='latin1')

    def show_prices(self, order):
        for item in order.cartitems:
            if item.show_price:
                return True
        return False

    def has_order_dimensions(self, order):
        """Checks if order has an item with dimensions.
        """
        for item in order.cartitems:
            if len(item.dimensions) > 0:
                return True
        return False

    def showStatus(self):
        registry = getUtility(IRegistry)
        shop_config = registry.forInterface(IShopConfiguration)
        return shop_config.show_status_column

    def getStatusSet(self):
        """Return the vocabulary for the currently
        selected StatusSet
        """
        status_set_name = self.shop_config.status_set
        status_set = getAdapter((self.context,), name=status_set_name)
        return status_set.vocabulary


class OrderView(BrowserView):
    """Displays a single order stored in a IOrderStorage
    """

    implements(IBrowserView, IPublishTraverse)
    template = ViewPageTemplateFile('templates/order_view.pt')

    def __init__(self, context, request):
        request.set('disable_border', True)
        registry = getUtility(IRegistry)
        self.shop_config = registry.forInterface(IShopConfiguration)
        self.order_storage_name = self.shop_config.order_storage
        super(OrderView, self).__init__(context, request)

    def __call__(self):
        new_status = self.request.form.get('form.widgets.status', '')
        try:
            new_status = int(new_status)
        except ValueError:
            new_status = None

        if new_status:
            order = self.getOrder()
            order.status = new_status
        return self.template()

    def getOrder(self, order_id=None):
        """Return the order identified by `order_id` or
        `self.order_id` (set during publishTraverse)
        """
        if not order_id:
            order_id = self.order_id
        order_storage = getUtility(IOrderStorage,
                                   name=self.order_storage_name)
        order = order_storage.getOrder(order_id)
        return order

    def has_order_dimensions(self):
        """Checks if order has an item with dimensions.
        """
        for item in self.getOrder().cartitems:
            if len(item.dimensions) > 0:
                return True
        return False

    def getStatus(self, order_id=None):
        """Return the human readable title of the status for
        this order.
        """
        order = self.getOrder()
        status = order.status

        status_set_name = self.shop_config.status_set
        status_set = getAdapter((self.context,), name=status_set_name)
        status_title = status_set.vocabulary.by_value[status].title
        return status_title

    def getStatusSet(self):
        """Return the vocabulary for the currently
        selected StatusSet
        """
        status_set_name = self.shop_config.status_set
        status_set = getAdapter((self.context,), name=status_set_name)
        return status_set.vocabulary

    def publishTraverse(self, request, id):
        """
        """
        order_view = OrderView(self.context, self.request)
        order_view.order_id = int(id)
        order_view.__name__ = str(id)
        # In Plone 3, somehow the view isn't acquisition wrapped
        # any more, therefore we fix that here
        return order_view.__of__(self.context)
