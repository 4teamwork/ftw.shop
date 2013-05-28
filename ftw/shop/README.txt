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
    >>> browser.handleErrors = False
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
    >>> browser.getControl('Save').click()

And we are done! We added a new 'Shop Item' content item.



Categorizing Shop Items
=======================

In this section we are demonstrating how to categorize shop content. For that we
first create a new Shop Category in the shop root called 'New' where we will list
new items in the shop.

    >>> browser.open(portal_url + '/shop')
    >>> browser.getLink(id='shopcategory').click()
    >>> browser.getControl('Title').value = 'New'
    >>> browser.getControl('Save').click()

Now let's assign the ShopItem we created before to this category. It will still be contained
in the 'Clothing' category we created it in, but also be listed in the 'New' category.

    >>> browser.open(portal_url + '/shop/clothing/t-shirt')
    >>> browser.getLink('Categories').click()
    >>> browser.getControl(name='categories:list').controls[1].click()
    >>> browser.getControl('Update').click()

If we now view the 'New' category, our item is being listed:
    >>> browser.open(portal_url + '/shop/new')
    >>> 'T-Shirt' in browser.contents
    True


Ranking items in categories
---------------------------

If we want to control the order in which items get listed in a category, we can set a rank 
for an item in a specific category. To demonstrate that, let's create a second item and also
add it to the 'New' category:

    >>> browser.open(portal_url + '/shop/clothing')
    >>> browser.getLink(id='shopitem').click()
    >>> browser.getControl('Title').value = 'Zope Sweater'
    >>> browser.getControl('Price').value = '15.00'
    >>> browser.getControl('SKU code').value = '9999'
    >>> browser.getControl('Save').click()

    >>> browser.getLink('Categories').click()
    >>> browser.getControl(name='categories:list').controls[1].click()
    >>> browser.getControl('Update').click()


Currently the item 'T-Shirt' is listed before the 'Zope Sweater', because if items have the same rank,
they get sorted alphabetically by title:

    >>> browser.open(portal_url + '/shop/new')
    >>> browser.contents.find('T-Shirt</a></h2>') < browser.contents.find('Zope Sweater</a></h2>')
    True

In order to change that order, we decrease the Sweater's rank for the 'New' category to 10,
putting it above the T-Shirt (which has a default rank of 100):

    >>> browser.open(portal_url + '/shop/clothing/zope-sweater')
    >>> browser.getLink('Categories').click()
    >>> rank_input = browser.getControl(name='rank_%s' % browser.getControl(name='categories:list').controls[1].optionValue)
    >>> rank_input.value = '10'
    >>> browser.getControl('Update').click()


Now the Zope Sweater is listed before the T-Shirt:

    >>> browser.open(portal_url + '/shop/new')
    >>> browser.contents.find('T-Shirt</a></h2>') < browser.contents.find('Zope Sweater</a></h2>')
    False



Buying a ShopItem
=================

Now let's buy the ShopItem 'T-Shirt' we added earlier. For that we click the "Add to cart"
button next to it, and then choose to checkout:

    >>> browser.open(portal_url + '/shop/clothing/t-shirt')
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

In the next step we're asked if we want to provide an alternative
shipping address. For now, we'll just skip that step.

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

