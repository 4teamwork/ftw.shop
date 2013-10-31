from ftw.testbrowser import browser


def add_to_cart():
    browser.find('Add to cart').click()
