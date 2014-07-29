from ftw.builder import Builder
from ftw.builder import builder_registry
from ftw.builder import create
from ftw.builder.archetypes import ArchetypesBuilder
from ftw.shop.interfaces import IShopCategory
from ftw.shop.portlets import cart
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import getSite
import transaction


class ShopItemBuilder(ArchetypesBuilder):

    portal_type = 'ShopItem'

    def before_create(self):
        super(ShopItemBuilder, self).before_create()
        if not IShopCategory.providedBy(self.container):
            self.container = create(Builder('shop category'))

builder_registry.register('shop item', ShopItemBuilder)


class ShopCategoryBuilder(ArchetypesBuilder):

    portal_type = 'ShopCategory'

builder_registry.register('shop category', ShopCategoryBuilder)


class ShopSupplierBuilder(ArchetypesBuilder):

    portal_type = 'Supplier'

builder_registry.register('supplier', ShopSupplierBuilder)


class CartPortletBuilder(object):

    def __init__(self, session):
        self.session = session
        self.container = getSite()
        self.arguments = {}
        self.manager_name = u'plone.rightcolumn'
        self.assignment_class = cart.Assignment

    def within(self, container):
        self.container = container
        return self

    def having(self, **kwargs):
        self.arguments.update(kwargs)
        return self

    def create(self):
        self.before_create()
        obj = self.create_portlet()
        self.after_create(obj)
        return obj

    def before_create(self):
        pass

    def create_portlet(self):
        manager = getUtility(IPortletManager,
                             name=self.manager_name,
                             context=self.container)
        assignments = getMultiAdapter((self.container, manager),
                                      IPortletAssignmentMapping,
                                      context=self.container)
        name = self.makeup_name(assignments)
        portlet = self.assignment_class(**self.arguments)
        assignments[name] = portlet
        return portlet

    def makeup_name(self, assignments):
        name = 'cartportlet'

        index = 1
        while name in assignments:
            name = 'cartportlet-%i' % index
            index += 1
        return name

    def after_create(self, obj):
        if self.session.auto_commit:
            transaction.commit()


builder_registry.register('cart portlet', CartPortletBuilder)
