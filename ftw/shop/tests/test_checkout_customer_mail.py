from ftw.builder import Builder
from ftw.builder import create
from ftw.shop.interfaces import IShopConfiguration
from ftw.shop.interfaces import IShopRoot
from ftw.shop.testing import FTW_SHOP_FUNCTIONAL_TESTING
from ftw.shop.tests.helpers import get_mail_header
from ftw.shop.tests.pages import checkout
from ftw.testbrowser import browsing
from ftw.testing.mailing import Mailing
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.registry.interfaces import IRegistry
from unittest2 import TestCase
from zope.component import getUtility
from zope.interface import alsoProvides
import email
import email.header
import transaction


class TestCheckoutMailToCustomer(TestCase):

    layer = FTW_SHOP_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        alsoProvides(self.portal, IShopRoot)
        create(Builder('cart portlet'))
        Mailing(self.portal).set_up()

    def checkout_and_get_mail(self, *items):
        mailing = Mailing(self.portal)
        for item in items:
            checkout.visit_checkout_with_one_item_in_cart(item)
        checkout.goto(checkout.ORDER_REVIEW).finish()
        self.assertEquals(1, len(mailing.get_messages()),
                          'Notifying shop owner is disabled by default, therefore'
                          ' only one mail (to the customer) should be sent.')
        return email.message_from_string(mailing.pop())

    def open_mail_in_browser(self, mail, browser):
        browser.open_html(mail.get_payload(decode=True))

    @browsing
    def test_customer_is_notified(self, browser):
        mail = self.checkout_and_get_mail()
        self.assertEquals(['Hugo Boss <hugo@boss.com>'], get_mail_header(mail, 'To'))
        self.assertEquals(['Your Webshop Order'], get_mail_header(mail, 'Subject'))

    @browsing
    def test_order_details(self, browser):
        self.open_mail_in_browser(self.checkout_and_get_mail(), browser)
        self.assertRegexpMatches(browser.css('#order-details').first.text,
                                 r'^Your order number is: \d*$')

    @browsing
    def test_personal_information(self, browser):
        self.open_mail_in_browser(self.checkout_and_get_mail(), browser)

        self.assertMultiLineEqual(
            '\n'.join(('Sir',
                       'Hugo Boss',
                       'Example Street 15',
                       '3000 Bern',
                       'Switzerland',
                       '',
                       'Email: hugo@boss.com',
                       'Phone: 001 0101 0101 01')),

            browser.css('#personal-information').first.text)

    @browsing
    def test_shipping_address(self, browser):
        self.open_mail_in_browser(self.checkout_and_get_mail(), browser)

        self.assertMultiLineEqual(
            '\n'.join(('Sir',
                       'Hugo Boss',
                       'Example Street 15',
                       '3000 Bern')),

            browser.css('#shipping-address').first.text)

    @browsing
    def test_product_is_listed_in_order_table(self, browser):
        item = create(Builder('shop item')
                      .titled('A pair of socks')
                      .having(skuCode='123.1',
                              price='12.90',
                              showPrice=True))

        self.open_mail_in_browser(self.checkout_and_get_mail(item), browser)

        self.assertEquals([{'Article number': '123.1',
                            'Product': 'A pair of socks',
                            'Price per item': '12.90',
                            'Quantity': '1',
                            'Total': '12.90'}],
                          browser.css('table').first.dicts(foot=False))

    @browsing
    def test_total_price_is_correct_in_order_table(self, browser):
        items = [create(Builder('shop item').having(price='10.00')),
                 create(Builder('shop item').having(price='5.00'))]

        self.open_mail_in_browser(self.checkout_and_get_mail(*items), browser)

        self.assertEquals([['VAT', '', '', '', '0.00'],
                           ['Total (incl.VAT)', '', '', '', '15.00']],
                          browser.css('table').first.lists(head=False, body=False))

    @browsing
    def test_default_contact_information(self, browser):
        self.open_mail_in_browser(self.checkout_and_get_mail(), browser)

        self.assertEquals(
            'For inquiries please contact us: E-Mail webshop@example.org',

            browser.css('#contact-information').first.text)

    @browsing
    def test_phone_in_contact_information_when_configured(self, browser):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IShopConfiguration)
        settings.phone_number = u'01 234 56 78'
        transaction.commit()

        self.open_mail_in_browser(self.checkout_and_get_mail(), browser)

        self.assertEquals(
            'For inquiries please contact us: Phone 01 234 56 78,'
            ' E-Mail webshop@example.org',

            browser.css('#contact-information').first.text)
