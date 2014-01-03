from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.shop import shopMessageFactory as _
from ftw.shop.interfaces import IShopItem
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


displayChoices = SimpleVocabulary(
    [SimpleTerm(value='always',
                token='always',
                title=_(u'label_always',
                        default=u'Always'),
                ),
     SimpleTerm(value='only_if_items',
                token='only_if_items',
                title=_(u'label_only_if_items',
                        default=u'Only if ShopItems available in current folder'),
                )
      ]
    )


class ICartPortlet(IPortletDataProvider):
    """A portlet that displays the shopping cart
    """
    mode = schema.Choice(title=_(u'Display mode'),
        description=_(u'Conditions under which portlet should be shown'),
        vocabulary=displayChoices,
        default='always'
        )


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ICartPortlet)

    def __init__(self, mode='always'):
        self.mode = mode

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u"label_cart_portlet", default=u"Cart Portlet")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('cart.pt')

    @property
    def available(self):
        # If the shopping cart contains items, we ALWAYS display the portlet
        if self.items_in_cart():
            return True

        if self.data.mode == 'only_if_items':
            # Only display portlet if there are shop items in current folder
            if self.context_has_shopitems():
                return True
            else:
                return False
        return True

    def context_has_shopitems(self):
        shopitem_ifaces = ['ftw.shop.interfaces.IShopItem',
                            'ftwshop.simplelayout.interfaces.IShopItemBlock']
        shop_contents = self.context.getFolderContents(
                            contentFilter={'object_provides': shopitem_ifaces})
        if shop_contents or IShopItem.providedBy(self.context):
            return True
        return False

    def items_in_cart(self):
        cart_view = getMultiAdapter((self.context, self.request), name='cart_view')
        return cart_view.cart_items()


class AddForm(base.AddForm):
    form_fields = form.Fields(ICartPortlet)
    label = _(u"label_add_cart_portlet",
              default=u"Add Shopping Cart Portlet")
    description = _(u"help_add_cart_portlet",
                default=u"This portlet displays the shopping cart contents.")

    def create(self, data):
        assignment = Assignment(**data)
        return assignment


class EditForm(base.EditForm):
    form_fields = form.Fields(ICartPortlet)
    label = _(u"Edit Shopping Cart portlet")
    description = _(u"This portlet displays the Shopping Cart.")
