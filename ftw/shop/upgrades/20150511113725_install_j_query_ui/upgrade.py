from ftw.upgrade import UpgradeStep


class InstallJQueryUI(UpgradeStep):
    """Install j query ui.
    """

    def __call__(self):
        self.install_upgrade_profile()
