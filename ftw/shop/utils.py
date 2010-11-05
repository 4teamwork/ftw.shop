from decimal import Decimal, InvalidOperation

def to_decimal(number):
    """Since SQLite doesn't support Decimal fields, trim the float it
    returns to two decimal places and convert it to Decimal. If that
    fails, return the total as-is."""
    try:
        return Decimal(str(number)[:str(number).find('.') + 3])
    except InvalidOperation:
        return number