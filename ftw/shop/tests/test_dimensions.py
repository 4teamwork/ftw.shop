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
                               .having(price='2.00',
                                       showPrice=True,
                                       selectable_dimensions='length_width')
                               .within(self.category))

    @browsing
    def test_dimension_input(self, browser):
        browser.login().visit(self.shopitem)

        self.assertEquals(
            2,
            len(browser.css('.dimensions-selection input[name="dimension:int"]')))

    @browsing
    def test_dimension_add_and_edit(self, browser):
        browser.login().visit(self.shopitem)

        dim = browser.css('.dimensions-selection input[name="dimension:int"]')
        dim[0].value = '2'
        dim[1].value = '3'
        browser.fill({'quantity:int': '1'}).submit()

        browser.open(self.portal, view='cart_edit')

        dim = browser.css('.dimensions-selection input')
        self.assertEquals('2', dim[0].value)
        self.assertEquals('3', dim[1].value)
        # check if price is correctly multiplied
        self.assertEquals('12.00', browser.css('form > div b span').first.text)

        dim[1].value = '4'

        browser.fill({'cart_update:method': 'submitted'}).submit()

        dim = browser.css('.dimensions-selection input')
        self.assertEquals('4', dim[1].value)
        self.assertEquals('16.00', browser.css('form > div b span').first.text)
