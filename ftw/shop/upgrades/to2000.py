from ftw.shop.interfaces import IShopRoot
from ftw.upgrade import UpgradeStep
from zope.interface import noLongerProvides


class RemoveShopRootInterface(UpgradeStep):
    """Remove IShopRoot from all objects providing it"""

    def __call__(self):
        catalog = self.getToolByName('portal_catalog')
        query = {'object_provides': IShopRoot.__identifier__}
        msg = 'Remove IShopRoot from objects providing it'
        for obj in self.objects(query, msg):
            noLongerProvides(obj, IShopRoot)
            catalog.reindexObject(obj, idxs=['object_provides'])

        if IShopRoot.providedBy(self.portal):
            noLongerProvides(self.portal, IShopRoot)
