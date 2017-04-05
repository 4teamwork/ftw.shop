import unittest

from zope.component import getMultiAdapter

from ftw.shop.tests.base import FtwShopTestCase
from pyquery import PyQuery as pq


class TestCategoryView(FtwShopTestCase):

    def afterSetUp(self):
        super(TestCategoryView, self).afterSetUp()

        self.category_view = getMultiAdapter((self.portal.shop.products,
                                 self.portal.REQUEST),
                                 name='view')

    def test_get_items(self):
        # Should be sorted aphabetically by Title
        self.assertEquals(self.category_view.getItems(),
                          [self.movie, self.tshirt, self.book])

    def test_single_item(self):
        item_datas = self.category_view.getItemDatas()
        item = item_datas[0]
        item_listing = self.category_view.single_item(item)

        pq_doc = pq(item_listing)
        self.assertEquals(len(pq_doc("input[name=skuCode][value='12345']")), 1)

    def test_one_variation(self):
        item_datas = self.category_view.getItemDatas()
        item = item_datas[2]
        item_listing = self.category_view.one_variation(item)
        self.assertTrue('Paperback' in item_listing)
        self.assertTrue('Hardcover' in item_listing)

        pq_doc = pq(item_listing)
        self.assertEquals(pq_doc("#var-Hardcover td")[2].text, 'b11')
        self.assertEquals(pq_doc("#var-Paperback td")[2].text, 'b22')

    def test_two_variations(self):
        item_datas = self.category_view.getItemDatas()
        item = item_datas[1]
        item_listing = self.category_view.two_variations(item)

        pq_doc = pq(item_listing)
        self.assertEquals(len(pq_doc('select[name=var1choice] option')), 3)
        self.assertEquals(len(pq_doc('select[name=var2choice] option')), 3)

    def test_get_item_datas(self):
        item_datas = self.category_view.getItemDatas()
        movie_data = item_datas[0]
        tshirt_data = item_datas[1]
        book_data = item_datas[2]

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


    def test_categories(self):
        categories = self.category_view.categories
        self.assertEquals(len(categories), 1)
        self.assertTrue(self.subcategory.id in categories[0]['url'])

    def test_category_contents(self):
        category_contents = self.category_view.category_contents
        self.assertEquals(len(category_contents), 4)
        self.assertTrue(self.movie in category_contents)
        self.assertTrue(self.book in category_contents)
        self.assertTrue(self.tshirt in category_contents)
        self.assertTrue(self.subcategory in category_contents)

    def test_category_contents_ordering(self):
        self.tshirt.setRankForCategory(self.portal.shop.products, 10)
        self.movie.setRankForCategory(self.portal.shop.products, 20)
        self.book.setRankForCategory(self.portal.shop.products, 30)
        self.subcategory.setRankForCategory(self.portal.shop.products, 40)

        category_contents = self.category_view.category_contents
        self.assertEquals(category_contents,
                          [self.tshirt,
                           self.movie,
                           self.book,
                           self.subcategory])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCategoryView))
    return suite
