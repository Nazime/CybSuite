from typing import TYPE_CHECKING

from cybsuite.consts import PATH_CYBSUITE
from koalak.plugin_manager import Plugin, PluginManager, abstract, field

if TYPE_CHECKING:
    from cybsuite.cyberdb import CyberDB

from cybsuite.cyberdb.cyberdb_scanner import CyberDBScanner

# FIXME: redo path once koalak.framework are ended
pm_home_path = PATH_CYBSUITE / "ingestors"


class BaseIngestor(Plugin, CyberDBScanner):
    extension: str = field()

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

    @classmethod
    def last_extension(cls):
        """
        Returns everything after the first dot, or the last extension if there are multiple.
        """
        # Check if there is at least one dot in the extension
        if "." in cls.extension:
            return "." + cls.extension.split(".", 1)[-1]
        else:
            # Return the entire string if no dot is present
            return cls.extension


pm_ingestors = PluginManager(
    "ingestors", base_plugin=BaseIngestor, entry_point="cybsuite.plugins"
)
