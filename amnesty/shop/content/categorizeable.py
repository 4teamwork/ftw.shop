from Persistence import PersistentMapping
from AccessControl import ClassSecurityInfo

class Categorizeable:
    """
    Mixin class for categorizeable objects
    """
    
    security = ClassSecurityInfo()
    defaultRank = 100
    category_relationship = 'shop_category'
    
    security.declareProtected("View", 'getRankForCategory')
    def getRankForCategory(self, category):
        """
        Get the object's rank for the specified category
        """
        if hasattr(self, '_categoryRanks'):
            return int(self._categoryRanks.get(category, self.defaultRank))
        return self.defaultRank

    
    security.declareProtected("Modify portal content", 'addToCategory')
    def setRankForCategory(self, category, rank):
        """
        Set the object's rank for the specified category
        """
        if not hasattr(self, '_categoryRanks') or not isinstance(self._categoryRanks, PersistentMapping):
            self._categoryRanks = PersistentMapping()
        self._categoryRanks[category] = rank


    security.declareProtected("Modify portal content", 'addToCategory')
    def addToCategory(self,category):
        """
        Add the object to a category.
        """
        self.addReference(category, self.category_relationship)


    security.declareProtected("Modify portal content", 'removeFromCategory')
    def removeFromCategory(self,category):
        """
        Remove the object from a category.
        """        
        self.deleteReference(category, self.category_relationship)


    security.declareProtected("View", 'listCategories')
    def listCategories(self):
        """
        List the categories where the object is registered.
        """       
        return self.getRefs(self.category_relationship)