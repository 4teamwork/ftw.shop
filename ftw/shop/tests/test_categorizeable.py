import unittest

from ftw.shop.content.categorizeable import Categorizeable
from ftw.shop.tests.base import FtwShopTestCase


class TestCategorizeable(FtwShopTestCase):
    
    def afterSetUp(self):
        super(TestCategorizeable, self).afterSetUp()

    def test_get_set_rank_for_category(self):
        mock_item = self.movie
        rank = mock_item.getRankForCategory(self.subcategory)
        self.assertEquals(rank, Categorizeable.defaultRank)
        
        mock_item.addToCategory(self.subcategory)
        mock_item.setRankForCategory(self.subcategory, 10)
        rank = mock_item.getRankForCategory(self.subcategory)
        self.assertEquals(rank, 10)
    
    def test_add_remove_category(self):
        mock_item = self.movie
        self.assertEquals(mock_item.listCategories(), [self.portal.shop.products])
        
        mock_item.addToCategory(self.subcategory)
        self.assertTrue(self.subcategory in mock_item.listCategories())
        
        mock_item.removeFromCategory(self.subcategory)
        self.assertTrue(self.subcategory not in mock_item.listCategories())



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCategorizeable))
    return suite
