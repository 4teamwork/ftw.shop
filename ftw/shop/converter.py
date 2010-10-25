import zope.component
import zope.schema

from z3c.form.converter import NumberDataConverter
from z3c.form import interfaces
from z3c.form.i18n import MessageFactory as _

class IntegerDataConverter(NumberDataConverter):
    """A data converter for integers."""
    zope.component.adapts(
        zope.schema.interfaces.IInt, interfaces.IWidget)
    type = int
    errorMessage = _('The entered value is not a valid integer literal.')

    def toWidgetValue(self, value):
        """See interfaces.IDataConverter"""
        if value is self.field.missing_value:
            return u''
        return int(value)
