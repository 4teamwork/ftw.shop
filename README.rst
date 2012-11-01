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

After you installed ``ftw.shop`` on your Plone site, you need to create a shop
root. This needs to be a folderish container that provides the marker interface
``IShopRoot``. This is where you will add your ShopCategory and ShopItem objects.

You can either do this yourself, by adding an ATFolder anywhere you like, and
use the ZMI "Interfaces" tab to make it provide the ``IShopRoot`` interface.

The easier alternative is using the ``initialize-shop-structure`` view on the
Plone site root. Simply visit

http://localhost:8080/Plone/initialize-shop-structure

and it will create an ATFolder named ``'shop'`` at the top level of your Plone
site and make it provide the ``IShopRoot`` interface.

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
