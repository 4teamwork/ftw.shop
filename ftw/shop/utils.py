import csv
import cStringIO
import codecs
from decimal import Decimal, InvalidOperation

from Acquisition import aq_inner, aq_parent
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.CMFCore.interfaces import ISiteRoot

from ftw.shop.interfaces import IShopRoot


def to_decimal(number):
    """Since SQLite doesn't support Decimal fields, trim the float it
    returns to two decimal places and convert it to Decimal. If that
    fails, return the number as-is."""
    try:
        if float(number) == 0.0:
            return Decimal('0.00')
    except ValueError:
        pass

    try:
        if str(number).find('.') == -1:
            return Decimal("%s.00" % number)
        return Decimal(str(number)[:str(number).find('.') + 3])
    except InvalidOperation:
        return number


def get_shop_root_object(context):
    """ Return the shop root object.
        If no shop root is defined, return the navigation root or the site
        root.
        Since this method traverses up the site until it finds an IShopRoot,
        it also works correctly on a site using LinguaPlone where there is
        one ShopRoot per language branch.
    """
    obj = aq_inner(context)
    while not IShopRoot.providedBy(obj) \
          and not INavigationRoot.providedBy(obj) \
          and not ISiteRoot.providedBy(obj):
        obj = aq_parent(obj)
    return obj


class UnicodeCSVWriter:
    """A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        for i, value in enumerate(row):
            if value is None:
                row[i] = ''
            else:
                try:
                    row[i] = str(value)
                except UnicodeEncodeError:
                    row[i] = value

        encoded_row = []
        for s in row:
            try:
                encoded_row.append(s.encode('utf-8'))
            except UnicodeDecodeError:
                # Already encoded
                encoded_row.append(s)

        self.writer.writerow(encoded_row)
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
