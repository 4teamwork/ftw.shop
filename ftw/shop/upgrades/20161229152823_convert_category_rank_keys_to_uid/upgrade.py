from ftw.shop.content.shopcategory import ShopCategory
from ftw.upgrade import UpgradeStep
from plone.uuid.interfaces import IUUID


class ConvertCategoryRankKeysToUid(UpgradeStep):
    """Convert category rank keys to uid.
    """

    def __call__(self):
        self.install_upgrade_profile()
        objs = self.objects(
            {
                'object_provides': [
                    'ftw.shop.interfaces.IShopCategory',
                    'ftw.shop.interfaces.IShopItem',
                ]
            },
            message='Converting category rank keys to uid',
        )
        for obj in objs:
            if hasattr(obj, '_categoryRanks'):
                for category, rank in obj._categoryRanks.items()[:]:
                    if isinstance(category, ShopCategory):
                        # Only convert the keys the first time the upgrade
                        # step is run.
                        obj._categoryRanks[IUUID(category)] = rank
                        del obj._categoryRanks[category]
