from koalak.plugin_manager import Plugin, PluginManager


class Prerequesite(Plugin):
    def __init__(self, db):
        self.cyberdb = db

    pass


pm_prerequesites = PluginManager("prerequesites", base_plugin=Prerequesite)


class DomainUser(Prerequesite):
    name = "domain_user"

    def run(self):
        return self.cyberdb.request("ad_user").exclude(password="")


class DomainUser(Prerequesite):
    name = "service"

    def run(self):
        return self.cyberdb.request("service")
