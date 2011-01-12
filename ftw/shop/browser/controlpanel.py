from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.z3cform.layout import wrap_form
from z3c.form import field, group

try:
    # plone.app.registry 1.0b1
    from plone.app.registry.browser.form import RegistryEditForm
    from plone.app.registry.browser.form import ControlPanelFormWrapper
except ImportError:
    # plone.app.registry 1.0b2+
    from plone.app.registry.browser.controlpanel import RegistryEditForm
    from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper

from ftw.shop.interfaces import IShopConfiguration
from ftw.shop import shopMessageFactory as _


class MailGroup(group.Group):
    label = u'Mail'
    fields = field.Fields(IShopConfiguration).select(
        'shop_email',
        'mail_bcc',
        'mail_subject_de',
        'mail_subject_en',
        'always_notify_shop_owner')


class CheckoutGroup(group.Group):
    label = u'Checkout'
    fields = field.Fields(IShopConfiguration).select(
        'payment_processor_step_group',
        'enabled_payment_processors',
        'contact_info_step_group',
        'shipping_address_step_group',
        'order_review_step_group')


class ShopConfigurationForm(RegistryEditForm, group.GroupForm):
    """Configuration form for the ftw.shop configlet
    """
    schema = IShopConfiguration
    fields = field.Fields(IShopConfiguration).omit('shop_email',
                                                   'mail_bcc',
                                                   'mail_subject_de',
                                                   'mail_subject_en',
                                                   'always_notify_shop_owner',
                                                   'payment_processor_step_group',
                                                   'enabled_payment_processors',
                                                   'contact_info_step_group',
                                                   'shipping_address_step_group',
                                                   'order_review_step_group')
    groups = (MailGroup, CheckoutGroup)
    label = _(u'label_shop_configuration', default=u"Shop configuration")

    def updateFields(self):
        super(ShopConfigurationForm, self).updateFields()

    def updateWidgets(self):
        super(ShopConfigurationForm, self).updateWidgets()

# BBB: For Plone3 compatibility, we need to override the template
# on the form wrapper, not the form itself, and use zope2's
# ViewPageTemplateFile, not zope3's
# See http://plone.org/products/dexterity/documentation/error/rendering-a-form-fails-with-attributeerror-str-object-has-no-attribute-other

ShopConfigurationView = wrap_form(ShopConfigurationForm, ControlPanelFormWrapper)
ShopConfigurationView.template = ViewPageTemplateFile('templates/controlpanel.pt')
