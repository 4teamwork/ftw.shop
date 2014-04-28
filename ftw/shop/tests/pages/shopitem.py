from ftw.testbrowser import browser


def add_to_cart(amount=1):
    form = browser.find('Add to cart').form
    form.fill({'quantity:int': str(amount)})
    form.find('Add to cart').click()

def edit_categories_link():
    return browser.css('#contentview-categories').first.find('Categories')
