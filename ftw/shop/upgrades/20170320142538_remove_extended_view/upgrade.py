from ftw.upgrade import UpgradeStep


class RemoveExtendedView(UpgradeStep):
    """Remove extended view.
    """

    def __call__(self):
        self.install_upgrade_profile()
        for obj in self.objects({
                'portal_type': ['Folder', 'ShopItem', 'ShopCategory']},
                'Remove old view from shop containers.'):

            if obj.getLayout() == 'compact_view':
                del obj.layout
