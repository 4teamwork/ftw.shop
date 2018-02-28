from ftw.builder import Builder
from ftw.builder import create
from ftw.shop.testing import FTW_SHOP_FUNCTIONAL_TESTING
from ftw.shop.tests.pages import cartportlet
from ftw.shop.tests.pages import checkout
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import plone
from ftw.testbrowser.pages import z3cform
from ftw.testing.mailing import Mailing
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles
from unittest2 import TestCase
import transaction


class TestBrowserCheckout(TestCase):

    layer = FTW_SHOP_FUNCTIONAL_TESTING

    def setUp(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)

        create(Builder('cart portlet'))
        Mailing(portal).set_up()
        transaction.commit()

    def tearDown(self):
        Mailing(self.layer['portal']).tear_down()

    @browsing
    def test_contact_information_fields_required(self, browser):
        checkout.visit_checkout_with_one_item_in_cart()
        checkout.next()
        checkout.assert_step(checkout.CONTACT_INFORMATION)
        form = browser.css('form.kssattr-formname-checkout-wizard').first

        self.assertEquals(
            {u'Title': ['Required input is missing.'],
             u'First Name': ['Required input is missing.'],
             u'Last Name': ['Required input is missing.'],
             u'Email': ['Required input is missing.'],
             u'Street/No.': ['Required input is missing.'],
             u'Phone number': ['Required input is missing.'],
             u'Zip Code': ['Required input is missing.'],
             u'City': ['Required input is missing.'],
             u'Country': ['Required input is missing.']},
            z3cform.erroneous_fields(form))

    @browsing
    def test_valid_email_address_required(self, browser):
        checkout.visit_checkout_with_one_item_in_cart()
        browser.fill({'Email': 'invalid.email.ch'})
        checkout.next()
        checkout.assert_step(checkout.CONTACT_INFORMATION)

        form = browser.css('form.kssattr-formname-checkout-wizard').first
        self.assertEquals(
            ['This email address is invalid.'],
            z3cform.erroneous_fields(form)[u'Email'])

    @browsing
    def test_contact_information_defaults_for_logged_in_user(self, browser):
        hugo = create(Builder('user').named('H\xc3\xbcgo', 'B\xc3\xb6ss'))
        browser.login(hugo)

        checkout.visit_checkout_with_one_item_in_cart()
        checkout.next()
        checkout.assert_step(checkout.CONTACT_INFORMATION)

        self.assertEquals(
            hugo.getProperty('fullname').split(' ')[1].decode('utf-8'),
            browser.css(
                '[name="contact_information.widgets.lastname"]').first.value)
        self.assertEquals(
            hugo.getProperty('fullname').split(' ')[0].decode('utf-8'),
            browser.css(
                '[name="contact_information.widgets.firstname"]').first.value)

    @browsing
    def test_contact_information_defaults_for_user_without_fullname(self,
                                                                    browser):
        browser.login()
        checkout.visit_checkout_with_one_item_in_cart()
        checkout.next()
        checkout.assert_step(checkout.CONTACT_INFORMATION)

        self.assertEquals(
            '',
            browser.css(
                '[name="contact_information.widgets.lastname"]').first.value)
        self.assertEquals(
            '',
            browser.css(
                '[name="contact_information.widgets.firstname"]').first.value)


    @browsing
    def test_submitting_contact_information_leads_to_shipping_address(self, browser):
        checkout.visit_checkout_with_one_item_in_cart()
        checkout.submit_valid_contact_info()
        checkout.assert_step(checkout.SHIPPING_ADDRESS)

    @browsing
    def test_shipping_address_is_prefilled(self, browser):
        checkout.visit_checkout_with_one_item_in_cart()
        checkout.fill_contact_info()
        browser.fill({'First Name': 'John',
                      'Last Name': 'Doe'})
        checkout.next()
        checkout.assert_step(checkout.SHIPPING_ADDRESS)
        self.assertEquals('John', browser.find('First Name').value)
        self.assertEquals('Doe', browser.find('Last Name').value)

    @browsing
    def test_back_on_shipping_address(self, browser):
        checkout.goto(checkout.SHIPPING_ADDRESS)
        checkout.back()
        checkout.assert_step(checkout.CONTACT_INFORMATION)

    @browsing
    def test_payment_processor_is_required(self, browser):
        checkout.goto(checkout.PAYMENT_PROCESSOR)
        checkout.next()
        checkout.assert_step(checkout.PAYMENT_PROCESSOR)
        form = browser.css('form.kssattr-formname-checkout-wizard').first

        # XXX: "Gegen Rechnung" should be translated to english
        self.assertEquals({u'Payment Processor': ['Required input is missing.']},
                          z3cform.erroneous_fields(form))

    @browsing
    def test_payment_processor_selection(self, browser):
        checkout.goto(checkout.PAYMENT_PROCESSOR)
        checkout.submit_valid_payment_processor()
        checkout.assert_step(checkout.ORDER_REVIEW)

    @browsing
    def test_back_on_payment_processor(self, browser):
        checkout.goto(checkout.PAYMENT_PROCESSOR)
        checkout.select_valid_payment_processor()
        checkout.back()
        checkout.assert_step(checkout.SHIPPING_ADDRESS)

    @browsing
    def test_order_review_shows_contact_information(self, browser):
        checkout.goto(checkout.ORDER_REVIEW)
        self.assertEquals(['Sir',
                           'Hugo Boss',
                           '',
                           'Example Street 15',
                           '',
                           '3000 Bern',
                           'Switzerland',
                           '',
                           'Email: hugo@boss.com',
                           'Phone: 001 0101 0101 01',
                           ''],
                          checkout.review_contact_information())

    @browsing
    def test_order_review_shows_shipping_address(self, browser):
        checkout.goto(checkout.ORDER_REVIEW)
        self.assertEquals(['Sir',
                           'Hugo Boss',
                           '',
                           'Example Street 15',
                           '',
                           '3000 Bern',
                           ''],
                          checkout.review_shipping_address())

    @browsing
    def test_order_review_shows_cart_items(self, browser):
        item = create(Builder('shop item')
                      .titled('Socks')
                      .having(description='A good pair of socks.',
                              price='10'))
        checkout.visit_checkout_with_one_item_in_cart(item=item)
        checkout.goto(checkout.ORDER_REVIEW)
        self.assertEquals([{'Product': 'Socks',
                            'Description': 'A good pair of socks.',
                            'Quantity': '1',
                            'Price per item': '10.00',
                            'Total': '10.00'}],
                          browser.css('table.cartListing').first.dicts(foot=False))

    @browsing
    def test_order_review_shows_correct_total(self, browser):
        pants = create(Builder('shop item').titled('Fancy Pants').having(price='35'))
        checkout.add_item_to_cart(pants, amount=2)
        socks = create(Builder('shop item').titled('Socks').having(price='12'))
        checkout.add_item_to_cart(socks, amount=3)

        cartportlet.order_link().click()
        checkout.goto(checkout.ORDER_REVIEW)

        # pants:  2 * 35 = 70
        # socks:  3 * 12 = 36
        # total          = 106

        table = browser.css('table.cartListing').first
        self.assertEquals([['VAT', '', '', '', '0.00'],
                           ['Total', '', '', '', '106.00']],
                          table.lists(head=False, body=False, foot=True))

    @browsing
    def test_back_on_order_review_leads_to_payment_processor(self, browser):
        checkout.goto(checkout.ORDER_REVIEW)
        checkout.back()
        checkout.assert_step(checkout.PAYMENT_PROCESSOR)

    @browsing
    def test_thankyou_page_when_finishing_checkout(self, browser):
        checkout.goto(checkout.ORDER_REVIEW).finish()
        self.assertEquals('thankyou', plone.view())
