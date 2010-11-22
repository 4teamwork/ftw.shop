Introduction
============

This is a full-blown functional test. The emphasis here is on testing what
the user may input and see, and the system is largely tested as a black box.
We use PloneTestCase to set up this test as well, so we have a full Plone site
to play with. We *can* inspect the state of the portal, e.g. using 
self.portal and self.folder, but it is often frowned upon since you are not
treating the system as a black box. Also, if you, for example, log in or set
roles using calls like self.setRoles(), these are not reflected in the test
browser, which runs as a separate session.

Being a doctest, we can tell a story here.

First, we must perform some setup. We use the testbrowser that is shipped
with Five, as this provides proper Zope 2 integration. Most of the 
documentation, though, is in the underlying zope.testbrower package.

    >>> from Products.Five.testbrowser import Browser
    >>> browser = Browser()
    >>> portal_url = self.portal.absolute_url()
    
The following is useful when writing and debugging testbrowser tests. It lets
us see all error messages in the error_log.

    >>> self.portal.error_log._ignored_exceptions = ()

With that in place, we can go to the portal front page and log in. We will
do this using the default user from PloneTestCase:

    >>> from Products.PloneTestCase.setup import portal_owner, default_password
    >>> browser.open(portal_url)
    
    >>> browser.getLink('Log in').click()
    >>> browser.getControl('Login Name').value = portal_owner
    >>> browser.getControl('Password').value = default_password
    >>> browser.getControl('Log in').click()

We then test that we are still on the portal front page:

    >>> browser.url == portal_url
    True

And we ensure that we get the friendly logged-in message:

    >>> "You are now logged in" in browser.contents
    True



Setting up a Shop Root
======================

First we need to set up a shop root folder where all Shop Categories and 
Shop Items will be contained:

    >>> browser.open(portal_url + '/initialize-shop-structure')
    >>> browser.open(portal_url + '/shop')

This handy view does that for us, creating a shop root folder called 'shop'
in the root of the site, setting the IShopRoot marker interface and
assigning the Shopping Cart portlet to it.
    

The Shop Category content type
==============================

In this section we are testing the Shop Category content type by performing
basic operations like adding and updating Shop Category content
items.

Adding a new Shop Category content item
---------------------------------------

We use the 'Shop Category' link from the 'Add new' menu to add a new 
shop category called 'Clothing':

    >>> browser.getLink(id='shopcategory').click()
    >>> browser.getControl('Title').value = 'Clothing'
    >>> browser.getControl('Save').click()

And we are done! We added a new 'Shop Category' content item to the portal.


Updating an existing Shop Category content item
-----------------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'A category for clothes'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'A category for clothes' in browser.contents
    True
    
    

The Shop Item content type
==========================

In this section we are testing the Shop Item content type by performing
basic operations like adding and updating Shop Item content items.

Adding a new Shop Item content item
-----------------------------------

We use the 'Shop Item' link from the 'Add new' menu to add a new shop item:
    
    >>> browser.getLink(id='shopitem').click()

Now we fill the form and submit it.

    >>> browser.getControl('Title').value = 'T-Shirt'
    >>> browser.getControl('Price').value = '7.00'
    >>> browser.getControl('SKU code').value = '7777'

We want this item to have two variation levels, 'Color' and 'Size', so we
set the respective fields:

    >>> browser.getControl('Variation 1 Attribute').value = 'Color'
    >>> browser.getControl('Variation 1 Values').value = 'Red\nBlue'
    >>> browser.getControl('Variation 2 Attribute').value = 'Size'
    >>> browser.getControl('Variation 2 Values').value = 'S\nM\nL'
    >>> browser.getControl('Save').click()

Now we need to fill in the data for the variations we defined. For that we
click on the 'Variations' tab and fill in the form:

    >>> browser.getLink('Variations').click()
    >>> browser.getControl(name='red-s-skuCode:required').value = '77771'
    >>> browser.getControl(name='red-m-skuCode:required').value = '77772'
    >>> browser.getControl(name='red-l-skuCode:required').value = '77773'
    >>> browser.getControl(name='blue-s-skuCode:required').value = '77774'
    >>> browser.getControl(name='blue-m-skuCode:required').value = '77775'
    >>> browser.getControl(name='blue-l-skuCode:required').value = '77776'
    >>> browser.getControl(name='red-l-price').value = '8.00'
    >>> browser.getControl(name='blue-l-price').value = '8.00'
    >>> browser.getControl('Save').click()

And we are done! We added a new 'Shop Item' content item with two variations.



Buying a ShopItem
=================

Now let's buy the ShopItem we just added. For that we click the "Add to cart"
button next to it, and then choose to checkout:

    >>> browser.getControl('Add to cart').click()
    >>> browser.getLink('Order').click()

Then we get asked our contact information, so we fill it in:

    >>> browser.getControl('Title').value = 'Mr.'
    >>> browser.getControl('First Name').value = 'Hugo'
    >>> browser.getControl('Last Name').value = 'Boss'
    >>> browser.getControl('Email').value = 'hugo.boss@example.org'
    >>> browser.getControl('Phone').value = '999 99 99'
    >>> browser.getControl('Street').value = 'Examplestreet 23'
    >>> browser.getControl('Zip Code').value = '12345'
    >>> browser.getControl('City').value = 'New York'
    >>> browser.getControl('Country').value = 'United States' 

    >>> browser.getControl('Next').click()

In the next step we're asked to select a payment processor. By default, only
payment by invoice ('Gegen Rechnung') is enabled.

    >>> browser.getControl('Gegen Rechnung').click()
    
    >>> browser.getControl('Next').click()

In the last step we get presented with an overview of our order, and are asked
to check if everything is correct and then conform the order by clicking
'Finish':
    
    >>> browser.getControl('Finish').click()
    >>> 'Order submitted' in browser.contents
    True
