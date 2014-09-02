from decimal import Decimal
from ftw.shop.tests.base import FtwShopTestCase
from ftw.shop.utils import to_decimal
from ftw.shop.utils import is_email_valid
from unittest2 import TestCase


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


class TestIsEmailValid(TestCase):

    def test_valid_addresses(self):
        self.assert_valid_email('john@doe.com')
        self.assert_valid_email('john.doe@gmail.com')
        self.assert_valid_email('j@doe.com')
        self.assert_valid_email('j.d@doe.com')
        self.assert_valid_email('me@john.doe.com')
        self.assert_valid_email('x@y.z')

    def test_invalid_addresses(self):
        self.assert_invalid_email('john@doe@gmail.com')
        self.assert_invalid_email('john.@gmail.com')
        self.assert_invalid_email('john@.gmail.com')
        self.assert_invalid_email('john@localhost')

    def assert_valid_email(self, address, msg=''):
        message = 'Expected email {0} to be valid'.format(address)
        if msg:
            message = ': '.join((message, msg))
        self.assertTrue(is_email_valid(address),
                        message)

    def assert_invalid_email(self, address, msg=''):
        message = 'Expected email {0} to be invalid'.format(address)
        if msg:
            message = ': '.join((message, msg))
        self.assertFalse(is_email_valid(address),
                         message)
