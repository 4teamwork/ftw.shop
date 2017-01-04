from AccessControl import ClassSecurityInfo
from ftw.shop.config import CATEGORY_RELATIONSHIP
from Persistence import PersistentMapping
from plone.uuid.interfaces import IUUID


class Categorizeable(object):
    """Mixin class for categorizeable objects
    """

    security = ClassSecurityInfo()
    defaultRank = 100

    security.declareProtected("View", 'getRankForCategory')

    def getRankForCategory(self, category):
        """Get the object's rank for the specified category
        """
        if hasattr(self, '_categoryRanks'):
            category_uuid = IUUID(category)
            return int(self._categoryRanks.get(category_uuid, self.defaultRank))
        return self.defaultRank


    security.declareProtected("Modify portal content", 'addToCategory')

    def setRankForCategory(self, category, rank):
        """Set the object's rank for the specified category
        """
        if not hasattr(self, '_categoryRanks') \
            or not isinstance(self._categoryRanks, PersistentMapping):
            self._categoryRanks = PersistentMapping()
        category_uuid = IUUID(category)
        self._categoryRanks[category_uuid] = rank


    security.declareProtected("Modify portal content", 'addToCategory')

    def addToCategory(self, category):
        """Add the object to a category.
        """
        self.addReference(category, CATEGORY_RELATIONSHIP)


    security.declareProtected("Modify portal content", 'removeFromCategory')

    def removeFromCategory(self, category):
        """Remove the object from a category.
        """
        self.deleteReference(category, CATEGORY_RELATIONSHIP)


    security.declareProtected("View", 'listCategories')

    def listCategories(self):
        """List the categories where the object is registered.
        """
        return self.getRefs(CATEGORY_RELATIONSHIP)
