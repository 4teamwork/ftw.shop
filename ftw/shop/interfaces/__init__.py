from zope.interface import Interface


class IShopRoot(Interface):
    """Marker interface for shop root folder."""

class IShoppable(Interface):
    """Marker interface for marking items as buyable."""

class IVariationConfig(Interface):
    """A component which provides variation configurations.
    """
    def getVariations():
        """Returns the variations stored on a ShopItem. 
        """
