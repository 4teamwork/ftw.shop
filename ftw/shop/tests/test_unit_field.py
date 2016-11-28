from ftw.builder import Builder
from ftw.builder import create
from ftw.shop.tests import FunctionalTestCase
from ftw.testbrowser import browsing


class TestUnitField(FunctionalTestCase):

    def setUp(self):
        super(TestUnitField, self).setUp()
        self.grant('Manager')

        self.folder = create(Builder('folder'))
        self.category = create(Builder('shop category').within(self.folder))
        self.shopitem = create(Builder('shop item')
                               .titled('Raindrops')
                               .having(showPrice=True,
                                       unit=u"Buckets")
                               .within(self.category))

    @browsing
    def test_unit_is_displayed(self, browser):
        browser.login().visit(self.shopitem)

        self.assertEquals(
            'Unit',
            browser.css('.shopItemTable th').first.text)
        self.assertEquals(
            'Buckets',
            browser.css('.shopItemTable td').first.text)
