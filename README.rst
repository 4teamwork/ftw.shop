Introduction
============

`ftw.shop` is a general purpose web shop product for Plone.
It features item variations, an extensible checkout wizard, pluggable
payment processors and optional SQLAlchemy storage.

`ftw.shop` supports Plone 4.x.


Features
========

- Basic shop functionality: Create a shop with categories and items, provide
  a shopping cart and checkout process guided by a wizard.
- Manage Item variations (flavors).
- Order Management
- Suppliers: Associate particular items or categories with a supplier that will
  be notified by email when those items are purchased.
- Pluggable payment processors
- Extensible checkout wizard: Add fields or whole steps to the checkout process.
- Flexible mail templates for order confirmations, owner and supplier
  notifications.


Installation
============

- Add ``ftw.shop`` to your buildout (or as dependency to a custom egg):

::

    [buildout]
    parts =
        instance
        ...

    [instance]
    ...
    eggs +=
        Plone
        ftw.shop

- Install default profile in portal_setup.


Configuration
============

When installing ``ftw.shop``, the Plone site is automatically configured as
shop root (``IShopRoot`` interface).
If you'd like another container to be the shop root you can change this by
removing the ``IShopRoot`` from the Plone site and let another container
provide it.

You might also want to add a shop cart portlet.

After that, most configuration can be done through the "Shop configuration"
control panel.


Links
=====

- Github project repository: https://github.com/4teamwork/ftw.shop
- Issue tracker: https://github.com/4teamwork/ftw.shop/issues
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.shop


Licensing
=========

This package is released under GPL Version 2.


Copyright
=========

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.shop`` is licensed under GNU General Public License, version 2.

.. image:: https://cruel-carlota.pagodabox.com/47108caebd3b96f110cd90b5044b34d6
   :alt: githalytics.com
   :target: http://githalytics.com/4teamwork/ftw.shop
