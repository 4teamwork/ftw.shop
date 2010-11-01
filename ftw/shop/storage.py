import time

from zope.interface import implements
from persistent import Persistent

from Products.CMFCore.permissions import ModifyPortalContent

from AccessControl import ClassSecurityInfo

from BTrees.IOBTree import IOBTree
try:
    from BTrees.LOBTree import LOBTree
    SavedDataBTree = LOBTree
except ImportError:
    SavedDataBTree = IOBTree
from BTrees.Length import Length

from ftw.shop.interfaces import IOrderStorage

security = ClassSecurityInfo()

class OrderStorage(Persistent):
    implements(IOrderStorage)
    
    def __init__(self):
        self._orderStorage = SavedDataBTree()
        self._orderCount = 0
        self._length = Length()

    def get(self, id):
        return self._orderStorage[id]
    
    def _addDataRow(self, value):
        """Adds a row of data to the internal storage
        """

        if isinstance(self._orderStorage, IOBTree):
            # 32-bit IOBTree; use a key which is more likely to conflict
            # but which won't overflow the key's bits
            id = self._orderCount
            self._orderCount += 1
        else:
            # 64-bit LOBTree
            id = self._orderCount
            self._orderCount += 1
#            id = int(time.time() * 1000)
#            while id in self._orderStorage: # avoid collisions during testing
#                id += 1
        self._orderStorage[id] = value
        self._length.change(1)
        return id



    security.declareProtected(ModifyPortalContent, 'addDataRow')
    def addDataRow(self, value):
        """ a wrapper for the _addDataRow method """
        
        return self._addDataRow(value)

    def __iter__(self):
        iter(self._orderStorage)
