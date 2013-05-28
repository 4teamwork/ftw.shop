"""Payment Processor Widget Implementation
"""
__docformat__ = "reStructuredText"

import zope.component
import zope.interface
import zope.schema.interfaces
from zope.i18n import translate
from zope.component import getAdapters

from z3c.form import interfaces
from z3c.form.widget import FieldWidget
from z3c.form.browser import widget
from z3c.form.browser.radio import RadioWidget

from ftw.shop.interfaces import IPaymentProcessorWidget
from ftw.shop.interfaces import IPaymentProcessor


class PaymentProcessorWidget(RadioWidget):
    """Input type radio payment processor widget implementation."""
    zope.interface.implementsOnly(IPaymentProcessorWidget)

    klass = u'paymentprocessor-widget'
    items = ()

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        super(PaymentProcessorWidget, self).update()
        widget.addFieldClass(self)
        self.items = []

        pp_list = list(getAdapters((self.form.context, self.request, None),
                                   IPaymentProcessor))
        pp_list = filter(lambda pp: pp[1].available(), pp_list)
        available_payment_processors = dict(pp_list)

        for count, term in enumerate(self.terms):
            if not term.value in available_payment_processors:
                continue
            checked = self.isChecked(term)
            id = '%s-%i' % (self.id, count)
            label = term.token
            if zope.schema.interfaces.ITitledTokenizedTerm.providedBy(term):
                label = translate(term.title, context=self.request,
                                  default=term.title)
            self.items.append(
                {'id': id, 'name': self.name + ':list', 'value': term.token,
                 'label': label, 'checked': checked,
                 'image': available_payment_processors[term.token].image,
                 'description': available_payment_processors[term.token].description})


@zope.component.adapter(zope.schema.interfaces.IField, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def PaymentProcessorFieldWidget(field, request):
    """IFieldWidget factory for PaymentProcessorWidget."""
    return FieldWidget(field, PaymentProcessorWidget(request))
