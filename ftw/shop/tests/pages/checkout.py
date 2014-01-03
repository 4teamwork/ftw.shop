from ftw.builder import Builder
from ftw.builder import create
from ftw.shop.tests.pages import cartportlet
from ftw.shop.tests.pages import shopitem
from ftw.testbrowser import browser


CONTACT_INFORMATION = '1. Contact Information'
SHIPPING_ADDRESS = '2. Shipping Address'
PAYMENT_PROCESSOR = '3. Payment Processor'
ORDER_REVIEW = '4. Order Review'


STEPS = [CONTACT_INFORMATION,
         SHIPPING_ADDRESS,
         PAYMENT_PROCESSOR,
         ORDER_REVIEW]


def add_item_to_cart(item, amount=1):
    browser.visit(item)
    shopitem.add_to_cart(amount=amount)


def visit_checkout_with_one_item_in_cart(item=None):
    if item is None:
        item = create(Builder('shop item'))
    add_item_to_cart(item)
    cartportlet.order_link().click()
    import checkout
    return checkout


def current_step():
    return browser.css('ul.wizard-steps > li.selected').first.text


def assert_step(expected):
    current = current_step()
    assert current == expected, \
        'Expected to be on step "%s", but current step is "%s"' % (
        expected, current)


def next():
    browser.find('Next').click()
    import checkout
    return checkout


def back():
    browser.find('Back').click()
    import checkout
    return checkout


def finish():
    browser.find('Finish').click()
    import checkout
    return checkout


def fill_contact_info():
    assert_step(CONTACT_INFORMATION)
    browser.fill({u'Title': 'Sir',
                  u'First Name': 'Hugo',
                  u'Last Name': 'Boss',
                  u'Email': 'hugo@boss.com',
                  u'Street/No.': 'Example Street 15',
                  u'Phone number': '001 0101 0101 01',
                  u'Zip Code': '3000',
                  u'City': 'Bern',
                  u'Country': 'Switzerland'})
    import checkout
    return checkout


def submit_valid_contact_info():
    return fill_contact_info().next()


def submit_valid_shipping_address():
    # defaults are already valid
    assert_step(SHIPPING_ADDRESS)
    return next()


def select_valid_payment_processor():
    assert_step(PAYMENT_PROCESSOR)
    # XXX: "Gegen Rechnung" should be translated to english
    browser.fill({'Gegen Rechnung': 'ftw.shop.InvoicePaymentProcessor'})
    import checkout
    return checkout


def submit_valid_payment_processor():
    return select_valid_payment_processor().next()


def goto(target):
    if browser.document is None:
        visit_checkout_with_one_item_in_cart()

    current = current_step()
    if current == target:
        import checkout
        return checkout

    current_index = STEPS.index(current)
    target_index = STEPS.index(target)
    assert current_index < target_index, \
        'Can not goto("%s"), currently on "%s" and can not backwards.' % (
        target, current)

    if current == CONTACT_INFORMATION:
        submit_valid_contact_info()
        return goto(target)

    elif current == SHIPPING_ADDRESS:
        submit_valid_shipping_address()
        return goto(target)

    elif current == PAYMENT_PROCESSOR:
        submit_valid_payment_processor()
        return goto(target)

    raise Exception('Failed to goto("%s"): unkown error' % target)


def review_contact_information():
    assert_step(ORDER_REVIEW)
    return browser.css('.contact-information li').text


def review_shipping_address():
    assert_step(ORDER_REVIEW)
    return browser.css('.shipping-address li').text
