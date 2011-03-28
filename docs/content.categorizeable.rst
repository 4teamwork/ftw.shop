:mod:`content.categorizeable`
===============================

.. automodule:: content.categorizeable
      :members:
      :undoc-members:

:class:`Categorizeable` is a Mixin Class that's being used to make ShopItems (as well as ShopCategories) categorizeable. Any Content Type that inherits
from :class:`Categorizeable` can be assigned to one or more Categories. Those assignments are stored as references on the Content Type.

By default, when a ShopItem is created it's automatically added to its containing Category, so every ShopItem is at least assigned to one category.

For more fine grained control over the order in which a Categories contents are listed, one can define the `rank` of an Item in a specific Category.
When the listing is being generated, the items will be ordered by their respective ranks, where a low rank puts the item at the top of the listing and vice-versa.