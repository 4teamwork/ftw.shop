from decimal import Decimal, InvalidOperation

from z3c.saconfig import named_scoped_session

Session = named_scoped_session('ftw.shop')


def create_session():
    """Returns a new sql session bound to the defined named scope.
    """

    return Session()

def to_decimal(number):
    """Since SQLite doesn't support Decimal fields, trim the float it
    returns to two decimal places and convert it to Decimal. If that
    fails, return the total as-is."""
    try:
        return Decimal(str(number)[:str(number).find('.') + 3])
    except InvalidOperation:
        return number