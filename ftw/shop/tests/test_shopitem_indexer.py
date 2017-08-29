from ftw.shop.tests.base import FtwShopTestCase


class TestShopIndexer(FtwShopTestCase):

    def test_sku_code_is_searchable(self):
        # default skuCode on ShopItem
        self.assertIn(self.movie.skuCode, self.movie.SearchableText())

        # skuCode in variation
        self.assertIn('b11', self.book.SearchableText())
        self.assertIn('b22', self.book.SearchableText())
