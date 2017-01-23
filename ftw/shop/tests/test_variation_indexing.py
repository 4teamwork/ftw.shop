from ftw.builder import Builder
from ftw.builder import create
from ftw.shop.tests import FunctionalTestCase
from ftw.testbrowser import browsing


class TestVariationIndexing(FunctionalTestCase):

    def setUp(self):
        super(TestVariationIndexing, self).setUp()
        self.grant('Manager')

        self.folder = create(Builder('folder'))
        self.category = create(Builder('shop category').within(self.folder))
        self.shopitem = create(Builder('shop item')
                               .titled('Raindrops')
                               .having(variation2_attribute="Farbe",
                                       variation1_values=('Rot', 'Blau'))
                               .within(self.category))

    @browsing
    def test_variations_are_searchable(self, browser):
        browser.visit()
        # check that we don't get any results by default
        browser.fill({'SearchableText': 'shouldnotfind'}).submit()
        self.assertEquals(0, len(browser.css('.searchResults dt a')))

        # check that we find our shopitem with the indexed color.
        browser.fill({'SearchableText': 'rot'}).submit()
        self.assertEquals(1, len(browser.css('.searchResults dt a')))
        self.assertEquals('Raindrops',
                          browser.css('.searchResults dt a').first.text)
