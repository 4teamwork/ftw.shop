# -*- coding: utf-8 -*-
import unittest
from datetime import datetime
from decimal import Decimal

from zope.component import getUtility

from ftw.shop.config import  ONLINE_PENDING_KEY
from ftw.shop.interfaces import IOrderStorage

from ftw.shop.tests.base import FtwShopTestCase

from ftw.shop.tests.base import MOCK_CUSTOMER
from ftw.shop.tests.base import MOCK_SHIPPING
from ftw.shop.tests.base import MOCK_CART

class TestBTreeStorage(FtwShopTestCase):
    
    def afterSetUp(self):
        super(TestBTreeStorage, self).afterSetUp()

                                 
    def test_btree_order_storage(self):
        btree_order_storage = getUtility(IOrderStorage, 'ftw.shop.BTreeOrderStorage')
        now = datetime.now()
        order_id = btree_order_storage.createOrder(status=ONLINE_PENDING_KEY, 
                                                 date=now,
                                                 customer_data=MOCK_CUSTOMER,
                                                 shipping_data=MOCK_SHIPPING,
                                                 cart_data=MOCK_CART,
                                                 total='8.30')
        self.assertEquals(order_id, 1)
        
        order = btree_order_storage.getOrder(order_id)
        self.assertEquals(order.order_id, order_id)
        self.assertEquals(order.status, ONLINE_PENDING_KEY)
        self.assertEquals(order.date, now)
        self.assertEquals(order.getTotal(), Decimal('8.30'))

        order_prefix = '%03d%s' % (now.timetuple().tm_yday + 500, now.strftime("%y"))
        order_number = '%s%04d' % (order_prefix, order_id)
        self.assertEquals(order.title, order_number)
        
        self.assertEquals(order.customer_title, MOCK_CUSTOMER['title'])
        self.assertEquals(order.customer_firstname, MOCK_CUSTOMER['firstname'])
        self.assertEquals(order.customer_lastname, MOCK_CUSTOMER['lastname'])
        self.assertEquals(order.customer_street1, MOCK_CUSTOMER['street1'])
        self.assertEquals(order.customer_street2, MOCK_CUSTOMER['street2'])
        self.assertEquals(order.customer_zipcode, MOCK_CUSTOMER['zipcode'])
        self.assertEquals(order.customer_city, MOCK_CUSTOMER['city'])
        self.assertEquals(order.customer_email, MOCK_CUSTOMER['email'])
        
        cart_items = order.cartitems
        self.assertEquals(cart_items[0].sku_code, MOCK_CART['some-uid']['skucode'])
        self.assertEquals(cart_items[0].quantity, MOCK_CART['some-uid']['quantity'])
        self.assertEquals(cart_items[0].title, MOCK_CART['some-uid']['title'])
        self.assertEquals(cart_items[0].price, Decimal(MOCK_CART['some-uid']['price']))
        self.assertEquals(cart_items[0].total, Decimal(MOCK_CART['some-uid']['total']))
        self.assertEquals(cart_items[0].supplier_name, MOCK_CART['some-uid']['supplier_name'])
        self.assertEquals(cart_items[0].supplier_email, MOCK_CART['some-uid']['supplier_email'])

        self.assertEquals(cart_items[0].order_id, order_id)
        self.assertEquals(cart_items[0].order, order)
        
    def test_get_field_names(self):
        btree_order_storage = getUtility(IOrderStorage, 'ftw.shop.BTreeOrderStorage')
        expected_field_names = ['customer_city',
                                 'customer_comments',
                                 'customer_company',
                                 'customer_country',
                                 'customer_email',
                                 'customer_firstname',
                                 'customer_lastname',
                                 'customer_phone',
                                 'customer_shipping_address',
                                 'customer_street1',
                                 'customer_street2',
                                 'customer_title',
                                 'customer_zipcode',
                                 'date',
                                 'order_id',
                                 'shipping_city',
                                 'shipping_firstname',
                                 'shipping_lastname',
                                 'shipping_company',
                                 'shipping_street1',
                                 'shipping_street2',
                                 'shipping_title',
                                 'shipping_zipcode',
                                 'status',
                                 'title',
                                 'total',
                                 'vat_amount']
        field_names = btree_order_storage.getFieldNames()
        self.assertEquals(sorted(field_names), sorted(expected_field_names))



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBTreeStorage))
    return suite
