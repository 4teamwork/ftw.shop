from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.z3cform.layout import wrap_form
from z3c.form import field, group
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper

from ftw.shop.interfaces import IShopConfiguration
from ftw.shop import shopMessageFactory as _


class MailGroup(group.Group):
    label = _('label_mail_group', default=u'Mail')
    fields = field.Fields(IShopConfiguration).select(
        'shop_email',
        'mail_bcc',
        'mail_subject',
        'always_notify_shop_owner')


class CheckoutGroup(group.Group):
    label = _('label_checkout_group', default=u'Checkout')
    fields = field.Fields(IShopConfiguration).select(
        'payment_processor_step_group',
        'enabled_payment_processors',
        'contact_info_step_group',
        'shipping_address_step_group',
        'order_review_step_group',
        'phone_number')


class VATGroup(group.Group):
    label = _('label_vat_group', default=u'VAT')
    fields = field.Fields(IShopConfiguration).select(
        'vat_enabled',
        'vat_number',
        'vat_rates')


class ShopConfigurationForm(RegistryEditForm, group.GroupForm):
    """Configuration form for the ftw.shop configlet
    """
    schema = IShopConfiguration
    fields = field.Fields(IShopConfiguration).omit('shop_email',
                                                   'mail_bcc',
                                                   'mail_subject',
                                                   'always_notify_shop_owner',
                                                   'payment_processor_step_group',
                                                   'enabled_payment_processors',
                                                   'contact_info_step_group',
                                                   'shipping_address_step_group',
                                                   'order_review_step_group',
                                                   'phone_number',
                                                   'vat_enabled',
                                                   'vat_number',
                                                   'vat_rates')
    groups = (MailGroup, CheckoutGroup, VATGroup)
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
