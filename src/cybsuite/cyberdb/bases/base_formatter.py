from typing import TYPE_CHECKING, Any

from cybsuite.consts import PATH_CYBSUITE
from koalak.plugin_manager import Plugin, PluginManager, abstract

if TYPE_CHECKING:
    from cybsuite.cyberdb import CyberDB


# FIXME: redo path once koalak.framework are ended
pm_home_path = PATH_CYBSUITE / "formats"


class BaseFormatter(Plugin):
    """Base class for format plugins that convert Django querysets to strings."""

    @abstract
    def format(self, queryset: Any) -> str:
        """Convert queryset to formatted string.

        Args:
            queryset: Django queryset to format

        Returns:
            Formatted string representation
        """
        pass


pm_formatters = PluginManager(
    "formatters", base_plugin=BaseFormatter, entry_point="cybsuite.plugins"
)
