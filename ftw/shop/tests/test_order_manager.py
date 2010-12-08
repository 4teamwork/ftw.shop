# -*- coding: utf-8 -*-
import unittest
from decimal import Decimal

from zope.component import  getMultiAdapter

from ftw.shop.interfaces import IOrderStorage
from ftw.shop.config import SESSION_ADDRESS_KEY, CART_KEY
from ftw.shop.tests.base import FtwShopTestCase
from ftw.shop.tests.base import MOCK_CUSTOMER, MOCK_CART

class TestOrderManager(FtwShopTestCase):
    
    def afterSetUp(self):
        super(TestOrderManager, self).afterSetUp()


    def test_download_csv(self):
        session = self.portal.REQUEST.SESSION
        # Create an order that can be used to test CSV generation
        order_manager = getMultiAdapter((self.portal.shop, self.portal.REQUEST),
                                   name=u'order_manager')
        session[SESSION_ADDRESS_KEY] = MOCK_CUSTOMER
        session[CART_KEY] = MOCK_CART
        session['order_confirmation'] = True
        session['payment_processor_choice'] = {'payment_processor': 'Test'}
        order_id = order_manager.addOrder()
        order = order_manager.getOrder(order_id)
        order_date = order.date
        order_number = order.title

        csv = order_manager.download_csv()
        csv_header = csv.split('\r\n')[0]
        csv_data = csv.split('\r\n')[1]

        expected_csv_header = 'order_id,title,status,total,date,' \
        'customer_title,customer_firstname,customer_lastname,customer_email,' \
        'customer_street1,customer_street2,customer_phone,customer_zipcode,'\
        'customer_city,customer_shipping_address,customer_country,' \
        'customer_newsletter,customer_comments,sku_code,quantity,title,' \
        'price,item_total,supplier_name,supplier_email'

        expected_csv_data = '1,%s,1,%s,%s,%s,%s,%s,%s,%s,,%s,%s,%s,,%s,False,' \
        ',%s,%s,%s,%s,%s,%s,%s' % (order_number,
                                     order.getTotal(),
                                     order_date,
                                     MOCK_CUSTOMER['title'],
                                     MOCK_CUSTOMER['firstname'],
                                     MOCK_CUSTOMER['lastname'],
                                     MOCK_CUSTOMER['email'],
                                     MOCK_CUSTOMER['street1'],
                                     MOCK_CUSTOMER['phone'],
                                     MOCK_CUSTOMER['zipcode'],
                                     MOCK_CUSTOMER['city'],
                                     MOCK_CUSTOMER['country'],
                                     MOCK_CART.keys()[0],
                                     MOCK_CART.values()[0]['quantity'],
                                     MOCK_CART.values()[0]['title'],
                                     MOCK_CART.values()[0]['price'],
                                     MOCK_CART.values()[0]['total'],
                                     MOCK_CART.values()[0]['supplier_name'],
                                     MOCK_CART.values()[0]['supplier_email'],)
        self.assertEquals(csv_header, expected_csv_header)
        self.assertEquals(csv_data, expected_csv_data)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestOrderManager))
    return suite
