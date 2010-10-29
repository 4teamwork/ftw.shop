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
        payment_processors = dict(list(getAdapters((None, None, None),
                                       IPaymentProcessor)))

        for count, term in enumerate(self.terms):
            checked = self.isChecked(term)
            id = '%s-%i' % (self.id, count)
            label = term.token
            if zope.schema.interfaces.ITitledTokenizedTerm.providedBy(term):
                label = translate(term.title, context=self.request,
                                  default=term.title)
            self.items.append(
                {'id': id, 'name': self.name + ':list', 'value': term.token,
                 'label': label, 'checked': checked,
                 'image': payment_processors[term.token].image,
                 'description': payment_processors[term.token].description})


@zope.component.adapter(zope.schema.interfaces.IField, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def PaymentProcessorFieldWidget(field, request):
    """IFieldWidget factory for PaymentProcessorWidget."""
    return FieldWidget(field, PaymentProcessorWidget(request))
