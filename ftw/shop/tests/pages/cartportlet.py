from ftw.testbrowser import browser


def is_visible():
    return len(browser.css('.portletCartPortlet')) > 0


def is_empty():
    empty = browser.css('.portletCartPortlet .cart-empty')
    if empty:
        return empty.first.text
    else:
        return False


def items():
    return browser.css('.portletCartPortlet .cart-items li a').text


def edit_cart_link():
    actions = browser.css('.portletCartPortlet .cartActions').first_or_none
    return actions and actions.find('Edit cart')


def order_link():
    actions = browser.css('.portletCartPortlet .cartActions').first_or_none
    return actions and actions.find('Order')


def order_manager_link():
    return browser.css('.portletCartPortlet').first.find('Order Manager')
