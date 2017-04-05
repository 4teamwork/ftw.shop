from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class SupplierMailView(BrowserView):
    """Browser view for generating mail to supplier containing
    only items from the order that are being supplied by that
    supplier.
    """

    template = ViewPageTemplateFile('templates/mail/supplier_notification.pt')

    def __call__(self, show_prices=False, has_order_dimensions=True,
                 order=None, shop_config=None, supplier=None):
        self.show_prices = show_prices
        self.has_order_dimensions = has_order_dimensions
        self.order = order
        self.shop_config = shop_config
        self.supplier = supplier

        return self.template(order=order,
                             shop_config=shop_config,
                             supplier=supplier,
                             show_prices=show_prices,
                             has_order_dimensions=has_order_dimensions)

    def cartitems(self):
        """Returns the subset of items from the order that are supplied
        by the given supplier.
        """
        filtered_items = []
        supplier_name, supplier_email = self.supplier
        for item_type in self.order.cartitems:
            if item_type.supplier_email == supplier_email \
            and item_type.supplier_name == supplier_name:
                filtered_items.append(item_type)
        return filtered_items

    def show_prices(self):
           for item in self.cartitems():
               if item.show_price:
                   return True
           return False

    def getTotal(self):
        items = self.cartitems()
        prices = [i.getPrice() * i.quantity for i in items]
        total = sum(prices)
        return total
