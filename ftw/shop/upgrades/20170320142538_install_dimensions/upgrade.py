from ftw.upgrade import UpgradeStep


class InstallDimensions(UpgradeStep):
    """Install dimensions.
    """

    def __call__(self):
        self.install_upgrade_profile()
