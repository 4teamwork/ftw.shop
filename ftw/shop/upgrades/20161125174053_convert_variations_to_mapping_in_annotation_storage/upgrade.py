from ftw.upgrade import UpgradeStep
from ftw.shop.interfaces import IVariationConfig


class ConvertVariationsToMappingInAnnotationStorage(UpgradeStep):
    """Convert variations to mapping in annotation storage.
    """

    def __call__(self):
        self.install_upgrade_profile()

        for item in self.objects({'portal_type': 'ShopItem'},
                                 'Migrate variations storage'):

            varConf = IVariationConfig(item)
            item_data = varConf.getVariationDict()
            varConf.updateVariationConfig(item_data)
