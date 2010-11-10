import unittest
from decimal import Decimal

from zope.component import getMultiAdapter

from ftw.shop.tests.base import FtwShopTestCase



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
        self.assertTrue('<input type="hidden" name="skuCode" value="12345" />' \
                            in item_listing)

    def test_one_variation(self):
        item_datas = self.book_view.getItemDatas()
        item = item_datas[0]
        item_listing = self.book_view.one_variation(item)
        self.assertTrue('Paperback' in item_listing)
        self.assertTrue('Hardcover' in item_listing)
        self.assertTrue('<input type="hidden" name="skuCode" value="b11" />' \
                            in item_listing)
        self.assertTrue('<input type="hidden" name="skuCode" value="b22" />' \
                            in item_listing)

    def test_two_variations(self):
        item_datas = self.tshirt_view.getItemDatas()
        item = item_datas[0]
        item_listing = self.tshirt_view.two_variations(item)
        self.assertTrue('<input type="hidden" name="skuCode" value="11" />' \
                            in item_listing)
    
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
        
    def test_edit_variations_view_call(self):
        book_edit_variations_html = self.book_edit_variations()
        expected_snippet = """<td>Hardcover</td>
                  <td><input type="checkbox" checked="checked" name="hardcover-active:boolean"></td>
                  <td><input type="text" class="number" name="hardcover-price" value="1.00"></td>
                  <td><input type="text" class="number" name="hardcover-stock:int" value="1"></td>
                  <td><input type="text" class="required uniqueSkuCode" name="hardcover-skuCode:required" value="b11">
                  </td>"""
        self.assertTrue(expected_snippet in book_edit_variations_html)
        
        tshirt_edit_variations_html = self.tshirt_edit_variations()
        expected_snippet = """<td>M</td>
                  <td><input type="checkbox" checked="checked" name="blue-m-active:boolean"></td>
                  <td><input type="text" class="number" name="blue-m-price" value="8.00"></td>
                  <td><input type="text" class="number" name="blue-m-stock:int" value="8"></td>
                  <td><input type="text" class="required uniqueSkuCode" name="blue-m-skuCode:required" value="88">
                  </td>"""
        self.assertTrue(expected_snippet in tshirt_edit_variations_html)
        
        self.portal.REQUEST['form'] = {}
        self.portal.REQUEST.form['form.submitted'] = True

        self.portal.REQUEST.form['hardcover-active'] = True
        self.portal.REQUEST.form['hardcover-price'] = '7.90'
        self.portal.REQUEST.form['hardcover-stock'] = 1
        self.portal.REQUEST.form['hardcover-skuCode'] = '1111'
        
        self.portal.REQUEST.form['paperback-active'] = True
        self.portal.REQUEST.form['paperback-price'] = '5'
        self.portal.REQUEST.form['paperback-stock'] = 2
        self.portal.REQUEST.form['paperback-skuCode'] = '2222'
        
        self.book_edit_variations()
        
        movie_data = self.book_vc.getVariationDict()

        self.assertEquals(movie_data['hardcover']['active'], True)
        self.assertEquals(movie_data['hardcover']['price'], Decimal('7.90'))
        self.assertEquals(movie_data['hardcover']['stock'], 1)
        self.assertEquals(movie_data['hardcover']['skuCode'], '1111')

        self.assertEquals(movie_data['paperback']['active'], True)
        self.assertEquals(movie_data['paperback']['price'], Decimal('5.00'))
        self.assertEquals(movie_data['paperback']['stock'], 2)
        self.assertEquals(movie_data['paperback']['skuCode'], '2222')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestShopItemViews))
    return suite
