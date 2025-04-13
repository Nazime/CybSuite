import typing

from koalak.plugin_manager import Plugin, PluginManager, abstract

if typing.TYPE_CHECKING:
    from cybsuite.cyberdb import CyberDB


class BaseReporter(Plugin):
    extension = None

    def __init__(self, cyberdb: "CyberDB", configuration: dict = None):
        if configuration is None:
            configuration = {}
        self.cyberdb = cyberdb
        self.configure(**configuration)

    @abstract
    def run(self, output):
        """Main method to run the reporter."""
        pass

    def do_processing(self):
        """Optional method to do processing before exporting the report."""
        pass

    def configure(self):
        """Configure the reporter. Must be implemented by the subclass if any configuration is needed."""
        pass


pm_reporter = PluginManager(
    "reporters", base_plugin=BaseReporter, entry_point="cybsuite.plugins"
)
