##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Text Widget Implementation

$Id: radio.py 78513 2007-07-31 23:03:47Z srichter $
"""
__docformat__ = "reStructuredText"

import zope.component
import zope.interface
import zope.schema
import zope.schema.interfaces
from zope.i18n import translate
from zope.component import getAdapters

from z3c.form import interfaces
from z3c.form.widget import SequenceWidget, FieldWidget
from z3c.form.browser import widget

from ftw.shop.interfaces import IFancyRadioWidget
from ftw.shop.interfaces import IPaymentProcessor

class FancyRadioWidget(widget.HTMLInputWidget, SequenceWidget):
    """Input type radio widget implementation."""
    zope.interface.implementsOnly(IFancyRadioWidget)

    klass = u'radio-widget'
    items = ()

    def isChecked(self, term):
        return term.token in self.value

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        super(FancyRadioWidget, self).update()
        widget.addFieldClass(self)
        self.items = []
        payment_processors = dict(list(getAdapters((None, None, None), IPaymentProcessor)))
        
        for count, term in enumerate(self.terms):
            checked = self.isChecked(term)
            id = '%s-%i' % (self.id, count)
            label = term.token
            if zope.schema.interfaces.ITitledTokenizedTerm.providedBy(term):
                label = translate(term.title, context=self.request,
                                  default=term.title)
            self.items.append(
                {'id':id, 'name':self.name + ':list', 'value':term.token,
                 'label':label, 'checked':checked, 
                 'fancy_image': payment_processors[term.token].fancy_image,
                 'fancy_label': payment_processors[term.token].fancy_label})


@zope.component.adapter(zope.schema.interfaces.IField, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def FancyRadioFieldWidget(field, request):
    """IFieldWidget factory for RadioWidget."""
    return FieldWidget(field, FancyRadioWidget(request))
