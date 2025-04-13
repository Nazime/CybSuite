import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, ClassVar, List, Optional

from cybsuite.consts import PATH_CYBSUITE
from cybsuite.cyberdb import CyberDBScanner
from koalak.plugin_manager import Plugin, PluginManager, abstract

pm_home_path = PATH_CYBSUITE / "reviewers"


@dataclass
class ReviewContext:
    """Context data that changes between hosts and plugins. Each plugin have access to it and context can be changed between each run and moment of the review flow."""

    hostname: str
    datetime: datetime
    host_extracts_path: Path
    # Global data is shared between all plugins of same type (ex: all windows reviewers)
    #  It is reset between evey type
    global_data: dict[str, Any] = field(default_factory=dict)
    # Plugin data is specific to a plugin, ann wants another plugin to use it
    plugin_data: dict[str, dict[str, Any]] = field(default_factory=dict)

    def get_plugin_data(self, plugin_name: str) -> dict[str, Any]:
        """Get data for a specific plugin, creating it if it doesn't exist."""
        if plugin_name not in self.plugin_data:
            self.plugin_data[plugin_name] = {}
        return self.plugin_data[plugin_name]


class BaseTypeReviewer(Plugin):
    def __init__(self):
        self.context = ReviewContext()

    def prepare_for_host(self):
        """Function called before starting reviewing a host"""
        pass

    def cleanup_for_host(self):
        """Function called after reviewing a host"""
        pass


pm_type_reviewers = PluginManager("type_reviewers", base_plugin=BaseTypeReviewer)


class BaseReviewer(Plugin, CyberDBScanner):
    type_reviewer: BaseTypeReviewer = None
    files: dict[str, Path] = {}

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            exceptions_path=pm_home_path / "exceptions" / f"{self.name}.exceptions.txt",
        )
        self.context: ReviewContext = None

    @abstract
    def do_run(self):
        """Main method to do core logic of the plugin.
        This method is called once per host."""
        pass

    def run(self, *args, **kwargs):
        return self.do_run(*args, **kwargs)

    def post_run(self, *args, **kwargs):
        return self.do_post_run(*args, **kwargs)

    def do_post_run(self):
        """Method called once all host have been reviewed. Used for consolidation."""
        pass

    # UTILS METHODS #
    @staticmethod
    def load_json(filepath, encoding=None):
        if encoding is None:
            encoding = "utf-8-sig"
        with open(filepath, encoding=encoding) as f:
            return json.load(f)

    def init(self):
        """Function called before starting reviewing all hosts of same type (ex: all windows reviewers)"""
        pass


# TODO: entry points!
pm_reviewers = PluginManager("reviewers", base_plugin=BaseReviewer)
