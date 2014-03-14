from ftw.builder import Builder
from ftw.builder import create
from ftw.shop.interfaces import IShopRoot
from ftw.shop.testing import FTW_SHOP_FUNCTIONAL_TESTING
from ftw.shop.tests.pages import manage_categories
from ftw.testbrowser import browsing
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from unittest2 import TestCase
import transaction


class TestBrowserManageCategories(TestCase):

    layer = FTW_SHOP_FUNCTIONAL_TESTING

    def setUp(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)

        shop_folder = create(Builder('folder')
                             .titled('shop')
                             .providing(IShopRoot))

        category_1 = create(Builder('shop category')
                            .within(shop_folder)
                            .titled('Category 1'))

        create(Builder('shop category')
               .within(category_1)
               .titled('Sub Category 1.1'))

        create(Builder('shop category')
               .within(category_1)
               .titled('Sub Category 1.2'))

        category_2 = create(Builder('shop category')
                            .within(shop_folder)
                            .titled('Category 2'))

        create(Builder('shop category')
               .within(category_2)
               .titled('Sub Category 2.1'))

        self.shop_item= create(Builder('shop item').within(category_1))

        transaction.commit()

    @browsing
    def test_manage_categories_shows_category_tree(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        manage_categories.visit_edit_categories(self.shop_item)
        category_tree = manage_categories.review_category_tree()
        self.assertEquals(
        [
            [
                ['Category 1', ''],
                ['Sub Category 1.1', 'Category 1 > Sub Category 1.1'],
                ['Sub Category 1.2', 'Category 1 > Sub Category 1.2']
            ],
            [
                ['Category 2', ''],
                ['Sub Category 2.1', 'Category 2 > Sub Category 2.1']
            ]
        ],
        category_tree)
