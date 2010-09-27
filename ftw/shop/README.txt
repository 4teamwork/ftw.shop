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

We have the login portlet, so let's use that.

    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()

Here, we set the value of the fields on the login form and then simulate a
submit click.

We then test that we are still on the portal front page:

    >>> browser.url == portal_url
    True

And we ensure that we get the friendly logged-in message:

    >>> "You are now logged in" in browser.contents
    True


-*- extra stuff goes here -*-
The Shop Category content type
===============================

In this section we are tesing the Shop Category content type by performing
basic operations like adding, updadating and deleting Shop Category content
items.

Adding a new Shop Category content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'Shop Category' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Shop Category').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Shop Category' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Shop Category Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'Shop Category' content item to the portal.

Updating an existing Shop Category content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New Shop Category Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New Shop Category Sample' in browser.contents
    True

Removing a/an Shop Category content item
--------------------------------

If we go to the home page, we can see a tab with the 'New Shop Category
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New Shop Category Sample' in browser.contents
    True

Now we are going to delete the 'New Shop Category Sample' object. First we
go to the contents tab and select the 'New Shop Category Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New Shop Category Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New Shop Category
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New Shop Category Sample' in browser.contents
    False

Adding a new Shop Category content item as contributor
------------------------------------------------

Not only site managers are allowed to add Shop Category content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'Shop Category' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Shop Category').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Shop Category' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Shop Category Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new Shop Category content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)


The Shop Item Variant content type
===============================

In this section we are tesing the Shop Item Variant content type by performing
basic operations like adding, updadating and deleting Shop Item Variant content
items.

Adding a new Shop Item Variant content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'Shop Item Variant' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Shop Item Variant').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Shop Item Variant' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Shop Item Variant Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'Shop Item Variant' content item to the portal.

Updating an existing Shop Item Variant content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New Shop Item Variant Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New Shop Item Variant Sample' in browser.contents
    True

Removing a/an Shop Item Variant content item
--------------------------------

If we go to the home page, we can see a tab with the 'New Shop Item Variant
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New Shop Item Variant Sample' in browser.contents
    True

Now we are going to delete the 'New Shop Item Variant Sample' object. First we
go to the contents tab and select the 'New Shop Item Variant Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New Shop Item Variant Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New Shop Item Variant
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New Shop Item Variant Sample' in browser.contents
    False

Adding a new Shop Item Variant content item as contributor
------------------------------------------------

Not only site managers are allowed to add Shop Item Variant content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'Shop Item Variant' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Shop Item Variant').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Shop Item Variant' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Shop Item Variant Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new Shop Item Variant content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)


The Shop Multi Item content type
===============================

In this section we are tesing the Shop Multi Item content type by performing
basic operations like adding, updadating and deleting Shop Multi Item content
items.

Adding a new Shop Multi Item content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'Shop Multi Item' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Shop Multi Item').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Shop Multi Item' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Shop Multi Item Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'Shop Multi Item' content item to the portal.

Updating an existing Shop Multi Item content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New Shop Multi Item Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New Shop Multi Item Sample' in browser.contents
    True

Removing a/an Shop Multi Item content item
--------------------------------

If we go to the home page, we can see a tab with the 'New Shop Multi Item
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New Shop Multi Item Sample' in browser.contents
    True

Now we are going to delete the 'New Shop Multi Item Sample' object. First we
go to the contents tab and select the 'New Shop Multi Item Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New Shop Multi Item Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New Shop Multi Item
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New Shop Multi Item Sample' in browser.contents
    False

Adding a new Shop Multi Item content item as contributor
------------------------------------------------

Not only site managers are allowed to add Shop Multi Item content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'Shop Multi Item' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Shop Multi Item').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Shop Multi Item' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Shop Multi Item Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new Shop Multi Item content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)


The Shop Item content type
===============================

In this section we are tesing the Shop Item content type by performing
basic operations like adding, updadating and deleting Shop Item content
items.

Adding a new Shop Item content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'Shop Item' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Shop Item').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Shop Item' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Shop Item Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'Shop Item' content item to the portal.

Updating an existing Shop Item content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New Shop Item Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New Shop Item Sample' in browser.contents
    True

Removing a/an Shop Item content item
--------------------------------

If we go to the home page, we can see a tab with the 'New Shop Item
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New Shop Item Sample' in browser.contents
    True

Now we are going to delete the 'New Shop Item Sample' object. First we
go to the contents tab and select the 'New Shop Item Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New Shop Item Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New Shop Item
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New Shop Item Sample' in browser.contents
    False

Adding a new Shop Item content item as contributor
------------------------------------------------

Not only site managers are allowed to add Shop Item content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'Shop Item' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Shop Item').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Shop Item' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Shop Item Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new Shop Item content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)



