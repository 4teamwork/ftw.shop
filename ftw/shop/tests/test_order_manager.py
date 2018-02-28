# -*- coding: utf-8 -*-
from ftw.shop.browser.ordermanager import COLUMN_TITLES
from ftw.shop.config import CART_KEY
from ftw.shop.config import SESSION_ADDRESS_KEY
from ftw.shop.config import SESSION_SHIPPING_KEY
from ftw.shop.tests.base import FtwShopTestCase
from ftw.shop.tests.base import MOCK_CART
from ftw.shop.tests.base import MOCK_CUSTOMER
from ftw.shop.tests.base import MOCK_SHIPPING
from plone import api
from zope.component import  getMultiAdapter
import unittest


class TestOrderManager(FtwShopTestCase):

    def afterSetUp(self):
        super(TestOrderManager, self).afterSetUp()

    def test_download_csv(self):
        session = self.portal.REQUEST.SESSION
        # Create an order that can be used to test CSV generation
        navroot = api.portal.get_navigation_root(self.portal)
        order_manager = getMultiAdapter((navroot, self.portal.REQUEST),
                                   name=u'order_manager')
        session[SESSION_ADDRESS_KEY] = MOCK_CUSTOMER
        session[SESSION_SHIPPING_KEY] = MOCK_SHIPPING
        session[CART_KEY] = MOCK_CART
        session['order_confirmation'] = True
        session['payment_processor_choice'] = {'payment_processor': 'Test'}
        order_id = order_manager.addOrder()
        order = order_manager.getOrder(order_id)
        order_date = order.date
        order_number = order.title

        # Call the OrderManager view to initialize om.order_results
        self.login()
        order_manager()

        csv = order_manager.download_csv()
        csv_header = csv.split('\r\n')[0]
        csv_data = csv.split('\r\n')[1]

        expected_header_ids = [
            'order_id',
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
            'customer_comments',
            'shipping_city',
            'shipping_company',
            'shipping_firstname',
            'shipping_lastname',
            'shipping_street1',
            'shipping_street2',
            'shipping_title',
            'shipping_zipcode',
            'vat_amount',
            'sku_code',
            'quantity',
            'dimensions',
            'title',
            'price',
            'item_total',
            'supplier_name',
            'supplier_email']
        expected_csv_header = ';'.join([COLUMN_TITLES[h] for h in expected_header_ids])

        expected_csv_data = ';'.join([
            '1',
            order_number,
            '1',
            str(order.getTotal()),
            str(order_date),
            MOCK_CUSTOMER['title'],
            MOCK_CUSTOMER['firstname'],
            MOCK_CUSTOMER['lastname'],
            MOCK_CUSTOMER['company'],
            MOCK_CUSTOMER['email'],
            MOCK_CUSTOMER['street1'],
            '',
            MOCK_CUSTOMER['phone'],
            MOCK_CUSTOMER['zipcode'],
            MOCK_CUSTOMER['city'],
            '',
            MOCK_CUSTOMER['country'],
            '',
            MOCK_SHIPPING['city'],
            MOCK_SHIPPING['company'],
            MOCK_SHIPPING['firstname'],
            MOCK_SHIPPING['lastname'],

            MOCK_SHIPPING['street1'],
            '',
            MOCK_SHIPPING['title'],
            MOCK_SHIPPING['zipcode'],

            MOCK_CART['some-uid']['vat_amount'],
            MOCK_CART['some-uid']['skucode'],
            str(MOCK_CART.values()[0]['quantity']),
            '2 Weight (g)',
            MOCK_CART.values()[0]['title'],
            str(MOCK_CART.values()[0]['price']),
            str(MOCK_CART.values()[0]['total']),
            MOCK_CART.values()[0]['supplier_name'],
            MOCK_CART.values()[0]['supplier_email'],])

        self.assertEquals(csv_header, expected_csv_header)
        self.assertEquals(csv_data, expected_csv_data)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestOrderManager))
    return suite
