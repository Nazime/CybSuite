from typing import TextIO

from cybsuite.consts import PATH_CYBSUITE
from koalak.plugin_manager import Plugin, PluginManager, abstract

# FIXME: redo path once koalak.framework are ended
pm_home_path = PATH_CYBSUITE / "formats"


# TODO: forein key are not useful anymore


class BaseFormatter(Plugin):
    """Base class for format plugins that write Django querysets to file-like objects."""

    include_hidden_fields = True  # When True show include hidden fields

    @abstract
    def format(self, data: list[dict], output: TextIO, fields: list[str]) -> None:
        """Write queryset to a file-like object in the specified format.

        Args:
            data: Data to format
            output: A file-like object supporting write operations
            fields: List of field names to include in the output

        Returns:
            None
        """
        pass


pm_formatters = PluginManager(
    "formatters", base_plugin=BaseFormatter, entry_point="cybsuite.plugins"
)
