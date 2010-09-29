from zope.interface import Interface


class IShopRoot(Interface):
    """Marker interface for shop root folder."""

class IShoppable(Interface):
    """Marker interface for marking items as buyable."""
