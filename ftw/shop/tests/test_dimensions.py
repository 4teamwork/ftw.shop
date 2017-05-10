from ftw.builder import Builder
from ftw.builder import create
from ftw.shop.browser.cart import validate_dimensions
from ftw.shop.content.shopitem import selectable_dimensions
from ftw.shop.tests import FunctionalTestCase
from ftw.testbrowser import browsing


class TestDimensions(FunctionalTestCase):

    def setUp(self):
        super(TestDimensions, self).setUp()
        self.grant('Manager')

        self.folder = create(Builder('folder'))
        self.category = create(Builder('shop category').within(self.folder))
        self.shopitem = create(Builder('shop item')
                               .titled('Raindrops')
                               .having(price='2.00',
                                       showPrice=True,
                                       selectable_dimensions='length_width_mm_mm2')
                               .within(self.category))

    @browsing
    def test_dimension_input(self, browser):
        browser.login().visit(self.shopitem)

        self.assertEquals(
            2,
            len(browser.css('.dimensions-selection input[name="dimension:float"]')))

    @browsing
    def test_dimension_add_and_edit(self, browser):
        browser.login().visit(self.shopitem)

        dim = browser.css('.dimensions-selection input[name="dimension:float"]')
        dim[0].value = '2.5'
        dim[1].value = '3'
        browser.fill({'quantity:int': '1'}).submit()

        browser.open(self.portal, view='cart_edit')

        dim = browser.css('.dimensions-selection input')
        self.assertEquals('2.5', dim[0].value)
        self.assertEquals('3', dim[1].value)
        # check if price is correctly multiplied
        self.assertEquals('15.00', browser.css('form > div b span').first.text)

        dim[1].value = '4'

        browser.fill({'cart_update:method': 'submitted'}).submit()

        dim = browser.css('.dimensions-selection input')
        self.assertEquals('4', dim[1].value)
        self.assertEquals('20.00', browser.css('form > div b span').first.text)

    def test_dimensions_validation(self):
        self.assertTrue(validate_dimensions([], []))
        self.assertTrue(validate_dimensions([1], [u'Length (mm)']))
        self.assertTrue(validate_dimensions(
            [1, 2, 3],
            [u"Length (mm)", u"Width (mm)", u"Thickness (mm)"]))
        self.assertTrue(validate_dimensions(['2'], [u'Length (mm)']))

        self.assertFalse(
            validate_dimensions([], [u'Length (mm)']),
            'There has to be the same amount of dimensions.')
        self.assertFalse(
            validate_dimensions([], None),
            'Both parameter have to be specified.')
        self.assertTrue(validate_dimensions(['2.2'], [u'Length (mm)']))
        self.assertFalse(
            validate_dimensions([-1], [u'Length (mm)']),
            'Negative dimensions are not allowed.')

    def test_dimensions_format(self):
        # this tests check if all selectable dimension configs are valid
        for key, config in selectable_dimensions.iteritems():
            self.assertIn('label', config)
            self.assertIn('dimensions', config)
            self.assertIn('dimension_unit', config)
            self.assertTrue(isinstance(config['dimensions'], list))

            if key == 'no_dimensions':
                continue

            if 'price_unit' in config:
                self.assertIn('price_to_dimension_modifier', config)

    @browsing
    def test_different_price_unit(self, browser):
        """ This tests creates a shopitem which takes g as input and displays
            the price in kg. The final price has to convert between those units.
        """
        self.priceitem = create(Builder('shop item')
                                .titled('Farbe')
                                .having(price='200.00',
                                        showPrice=True,
                                        selectable_dimensions='weight_g_kg')
                                .within(self.category))

        browser.login().visit(self.priceitem)

        dim = browser.css('.dimensions-selection input[name="dimension:float"]')
        dim[0].value = '150'
        browser.fill({'quantity:int': '1'}).submit()

        browser.open(self.portal, view='cart_edit')

        self.assertEquals('30.00', browser.css('form > div b span').first.text)
