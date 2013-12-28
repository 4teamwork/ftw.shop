from ftw.shop.tests.base import FtwShopTestCase
from pyquery import PyQuery as pq
from zope.component import getMultiAdapter
import unittest


class TestShopItemViews(FtwShopTestCase):

    def afterSetUp(self):
        super(TestShopItemViews, self).afterSetUp()

        self.movie_view = getMultiAdapter((self.movie,
                                 self.portal.REQUEST),
                                 name='view')
        self.book_view = getMultiAdapter((self.book,
                                 self.portal.REQUEST),
                                 name='view')
        self.tshirt_view = getMultiAdapter((self.tshirt,
                                 self.portal.REQUEST),
                                 name='view')

        self.book_edit_variations = getMultiAdapter((self.book,
                                 self.portal.REQUEST),
                                 name='edit_variations')

        self.tshirt_edit_variations = getMultiAdapter((self.tshirt,
                                 self.portal.REQUEST),
                                 name='edit_variations')


    def test_get_items(self):
        self.assertEquals(self.movie_view.getItems(),
                          [self.movie])

    def test_single_item(self):
        item_datas = self.movie_view.getItemDatas()
        item = item_datas[0]
        item_listing = self.movie_view.single_item(item)

        pq_doc = pq(item_listing)
        self.assertEquals(len(pq_doc("input[name=skuCode][value=12345]")), 1)

    def test_one_variation(self):
        item_datas = self.book_view.getItemDatas()
        item = item_datas[0]
        item_listing = self.book_view.one_variation(item)
        self.assertTrue('Paperback' in item_listing)
        self.assertTrue('Hardcover' in item_listing)

        pq_doc = pq(item_listing)
        self.assertEquals(len(pq_doc("input[name=skuCode][value=b11]")), 1)
        self.assertEquals(len(pq_doc("input[name=skuCode][value=b22]")), 1)

    def test_two_variations(self):
        item_datas = self.tshirt_view.getItemDatas()
        item = item_datas[0]
        item_listing = self.tshirt_view.two_variations(item)
        pq_doc = pq(item_listing)
        self.assertEquals(len(pq_doc("input[name=skuCode][value=11]")), 1)

    def test_get_item_datas(self):
        movie_data = self.movie_view.getItemDatas()[0]
        book_data = self.book_view.getItemDatas()[0]
        tshirt_data = self.tshirt_view.getItemDatas()[0]

        self.assertEquals(movie_data['description'],
                          'A Shop Item with no variations')
        self.assertEquals(movie_data['hasVariations'], False)
        self.assertEquals(movie_data['imageTag'], None)
        self.assertEquals(movie_data['skuCode'], '12345')
        self.assertEquals(movie_data['price'], '7.15')
        self.assertEquals(movie_data['title'], 'A Movie')
        self.assertEquals(movie_data['varConf'], None)
        self.assertEquals(movie_data['variants'], None)

        self.assertEquals(book_data['description'],
                          'A Shop Item with one variation')
        self.assertEquals(book_data['hasVariations'], True)
        self.assertEquals(book_data['imageTag'], None)
        self.assertEquals(book_data['skuCode'], None)
        self.assertEquals(book_data['price'], None)
        self.assertEquals(book_data['title'], 'Professional Plone Development')
        self.assertTrue(book_data['varConf'])
        self.assertEquals(book_data['variants'], None)

        self.assertEquals(tshirt_data['description'],
                          'A Shop Item with two variations')
        self.assertEquals(tshirt_data['hasVariations'], True)
        self.assertEquals(tshirt_data['imageTag'], None)
        self.assertEquals(tshirt_data['skuCode'], None)
        self.assertEquals(tshirt_data['price'], None)
        self.assertEquals(tshirt_data['title'], 'A T-Shirt')
        self.assertTrue(tshirt_data['varConf'])
        self.assertEquals(tshirt_data['variants'], None)

    def test_get_variations_config(self):
        movie_vc = self.movie_view.getVariationsConfig()
        book_vc = self.book_view.getVariationsConfig()
        tshirt_vc = self.tshirt_view.getVariationsConfig()

        self.assertEquals(movie_vc.getVariationAttributes(), [])
        self.assertEquals(book_vc.getVariationAttributes(), ['Cover'])
        self.assertEquals(tshirt_vc.getVariationAttributes(), ['Color', 'Size'])


    def test_variations_order(self):
        var1_values = self.tshirt_vc.getVariation1Values()
        self.assertEquals(var1_values, ('Red', 'Green', 'Blue'))

        item_datas = self.tshirt_view.getItemDatas()
        item = item_datas[0]
        item_listing = self.tshirt_view.two_variations(item)

        pq_doc = pq(item_listing)
        all_sku_codes = pq_doc('input[name=skuCode]')
        red_s = [e for e in all_sku_codes if e.value=='11'][0]
        green_s = [e for e in all_sku_codes if e.value=='44'][0]
        blue_s = [e for e in all_sku_codes if e.value=='77'][0]

        self.assertTrue(all_sku_codes.index(red_s) < all_sku_codes.index(green_s) \
            and all_sku_codes.index(green_s) < all_sku_codes.index(blue_s))

        # Now we swap 'Red' and 'Blue' and check if the listing reflects
        # the new order
        self.tshirt.Schema().getField('variation1_values').set(self.tshirt, ['Blue', 'Green', 'Red'])

        item_datas = self.tshirt_view.getItemDatas()
        item = item_datas[0]
        item_listing = self.tshirt_view.two_variations(item)

        pq_doc = pq(item_listing)
        all_sku_codes = pq_doc('input[name=skuCode]')
        red_s = [e for e in all_sku_codes if e.value=='11'][0]
        green_s = [e for e in all_sku_codes if e.value=='44'][0]
        blue_s = [e for e in all_sku_codes if e.value=='77'][0]

        self.assertTrue(all_sku_codes.index(red_s) > all_sku_codes.index(green_s) \
            and all_sku_codes.index(green_s) > all_sku_codes.index(blue_s))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestShopItemViews))
    return suite
