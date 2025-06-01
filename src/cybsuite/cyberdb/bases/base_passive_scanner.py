from typing import TYPE_CHECKING

from cybsuite.consts import PATH_CYBSUITE
from koalak.plugin_manager import Plugin, PluginManager, abstract, field

if TYPE_CHECKING:
    from cybsuite.cyberdb import CyberDB

from cybsuite.cyberdb.cyberdb_scanner import CyberDBScanner

# FIXME: redo path once koalak.framework are ended
pm_home_path = PATH_CYBSUITE / "passive_scanners"


class BasePassiveScanner(Plugin, CyberDBScanner):
    def __init__(self, cyberdb: "CyberDB"):
        super().__init__(
            cyberdb,
            # TODO: double check if exceptions_path are working
            exceptions_path=pm_home_path / "exceptions" / f"{self.name}.exceptions.txt",
        )

    def run(self, *args, **kwargs):
        return self.do_run(*args, **kwargs)

    @abstract
    def do_run(self, *args, **kwargs):
        pass


pm_passive_scanners = PluginManager(
    "passive_scanners", base_plugin=BasePassiveScanner, entry_point="cybsuite.plugins"
)
