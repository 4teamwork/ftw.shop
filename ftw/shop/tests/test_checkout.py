from datetime import datetime
from ftw.shop.browser.cart import CartView
from ftw.shop.browser.checkout import CheckoutView
from ftw.shop.browser.checkout import CheckoutWizard
from ftw.shop.config import  ONLINE_PENDING_KEY
from ftw.shop.interfaces import IOrderStorage
from ftw.shop.tests.base import FtwShopTestCase
from ftw.shop.tests.base import MOCK_CART
from ftw.shop.tests.base import MOCK_CART_TWO_SUPPLIERS
from ftw.shop.tests.base import MOCK_CUSTOMER
from ftw.shop.tests.base import MOCK_SHIPPING
from plone import api
from zope.component import getMultiAdapter, getUtility
import unittest


class TestCheckout(FtwShopTestCase):

    def afterSetUp(self):
        super(TestCheckout, self).afterSetUp()
        self.checkout_view = CheckoutView(self.portal, self.portal.REQUEST)
        self.wizard = CheckoutWizard(self.portal, self.portal.REQUEST)

    def test_checkout_view(self):
        self.assertTrue(isinstance(self.checkout_view, CheckoutView))
        self.assertTrue(isinstance(self.portal.REQUEST['cart_view'], CartView))

    def test_wizard_steps(self):
        wizard = self.wizard
        steps = wizard.steps
        default_contact_info_step = steps[0]
        default_shipping_address_step = steps[1]
        default_payment_processor_choice_step = steps[2]
        default_order_review_step = steps[3]

        self.assertEquals(default_contact_info_step.title,
                          u'title_default_contact_info_step')
        self.assertEquals(default_shipping_address_step.title,
                        u'title_default_shipping_address_step')
        self.assertEquals(default_payment_processor_choice_step.title,
                          u'title_default_payment_processor_step')
        self.assertEquals(default_order_review_step.title,
                          u'title_default_order_review_step')

    def test_send_ordermails_one_supplier(self):
        btree_order_storage = getUtility(IOrderStorage, 'ftw.shop.BTreeOrderStorage')
        now = datetime.now()
        oid1 = btree_order_storage.createOrder(
            status=ONLINE_PENDING_KEY,
            date=now,
            customer_data=MOCK_CUSTOMER,
            shipping_data=MOCK_SHIPPING,
            cart_data=MOCK_CART,
            total='8.30')

        navroot = api.portal.get_navigation_root(self.portal)
        omanager = getMultiAdapter((navroot, self.portal.REQUEST),
                                   name=u'order_manager')

        # send order mail
        omanager.sendOrderMails(oid1)
        messages = omanager.context.MailHost.messages
        self.assertEqual(len(messages), 2)
        self.assertTrue('To: Supplier Name <supplier@example.org>' in messages[1])

    def test_send_ordermails_two_suppliers(self):
        btree_order_storage = getUtility(IOrderStorage, 'ftw.shop.BTreeOrderStorage')
        now = datetime.now()
        oid2 = btree_order_storage.createOrder(
            status=ONLINE_PENDING_KEY,
            date=now,
            customer_data=MOCK_CUSTOMER,
            shipping_data=MOCK_SHIPPING,
            cart_data=MOCK_CART_TWO_SUPPLIERS,
            total='8.30')

        navroot = api.portal.get_navigation_root(self.portal)
        omanager = getMultiAdapter((navroot, self.portal.REQUEST),
                                   name=u'order_manager')

        # send order mail
        omanager.sendOrderMails(oid2)
        messages = omanager.context.MailHost.messages
        self.assertEqual(len(messages), 3)
        self.assertTrue('To: Supplier Name <other@example.org>' in messages[1])
        self.assertTrue('To: Supplier Name <supplier@example.org>' in messages[2])


    # def test_default_contact_info_step(self):
    #     wizard = self.wizard
    #     session = self.portal.REQUEST.SESSION
    #
    #     # Test form prefill from data in session
    #     session[SESSION_ADDRESS_KEY] = MOCK_CUSTOMER
    #
    #     step = DefaultContactInfoStep(self.portal,
    #                                   self.portal.REQUEST,
    #                                   wizard)
    #     for key in MOCK_CUSTOMER.keys():
    #         self.assertEquals(step.fields[key].field.default,
    #                           MOCK_CUSTOMER[key])
    #
    #
    #     # Test form prefill from cookie
    #     cookie_data = base64.b64encode(simplejson.dumps(MOCK_CUSTOMER))
    #     self.portal.REQUEST[COOKIE_ADDRESS_KEY] = cookie_data
    #     step = DefaultContactInfoStep(self.portal,
    #                                   self.portal.REQUEST,
    #                                   wizard)
    #     for key in MOCK_CUSTOMER.keys():
    #         self.assertEquals(step.fields[key].field.default,
    #                           MOCK_CUSTOMER[key])




def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCheckout))
    return suite
