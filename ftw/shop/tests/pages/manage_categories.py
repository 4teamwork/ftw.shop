from ftw.builder import Builder
from ftw.builder import create
from ftw.shop.tests.pages import shopitem
from ftw.testbrowser import browser


def visit_edit_categories(item=None):
    if item is None:
        item = create(Builder('shop item'))
    browser.visit(item)
    shopitem.edit_categories_link().click()


def review_category_tree():
    category_tree = []
    listing_tables = browser.css('.categoryListing')[1:]
    for table in listing_tables:
        category_branch = []
        for row in table.css('tr'):
            expand_toggle, checkbox, name, rank = row.css('td')
            item_title = name.text
            breadcrumb_title = name.css('a').first.attrib.get('title', '')
            category_branch.append([item_title, breadcrumb_title])

        category_tree.append(category_branch)
    return category_tree