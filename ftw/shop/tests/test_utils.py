import unittest
from decimal import Decimal
from ftw.shop.utils import to_decimal

from ftw.shop.tests.base import FtwShopTestCase


class TestUtils(FtwShopTestCase):
    
    def afterSetUp(self):
        super(TestUtils, self).afterSetUp()
 
    def test_to_decimal(self):
        self.assertEquals(to_decimal('10.00'), Decimal('10.00'))
        self.assertEquals(to_decimal('123'), Decimal('123.00'))
        self.assertEquals(to_decimal('50.25999'), Decimal('50.25'))
        self.assertEquals(to_decimal('NaN'), 'NaN')
        self.assertEquals(to_decimal('invalid'), 'invalid')

        self.assertEquals(to_decimal(0), Decimal('0.00'))
        self.assertEquals(to_decimal(Decimal('0E-10')), Decimal('0.00'))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUtils))
    return suite
