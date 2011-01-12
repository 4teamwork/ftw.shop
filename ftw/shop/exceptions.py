class MissingCustomerInformation(Exception):
    """Gets raised if trying to add an order when customer information has
    not been supplied yet.
    """
    pass


class MissingShippingAddress(Exception):
    """Gets raised if trying to add an order when shipping address has
    not been supplied yet.
    """
    pass


class MissingOrderConfirmation(Exception):
    """Gets raised if trying to add an order but the customer hasn't confirmed
    the order in the review step yet.
    """
    pass


class MissingPaymentProcessor(Exception):
    """Gets raised if trying to add an order but the customer hasn't selected
    a payment processor yet.
    """
    pass
