from ftw.upgrade import UpgradeStep


class AddPriceCalcJS(UpgradeStep):
    """Add price calc js.
    """

    def __call__(self):
        self.install_upgrade_profile()
