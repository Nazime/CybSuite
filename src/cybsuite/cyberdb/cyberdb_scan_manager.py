import contextlib
import time
import traceback
from typing import Callable, Iterable, Optional, Type

import rich
from cybsuite.core.logger import get_rich_console
from koalak.plugin_manager import Plugin, PluginManager
from rich.progress import Progress, track

from .cybsmodels import CyberDB


class Nothing:
    """Class used to avoid using None in code when it's ambigious"""

    pass


class CyberDBScanManager:
    def __init__(self, cyberdb: Optional[CyberDB] = None, quiet: Optional[bool] = None):
        """Initialize the CyberDBScanManager.

        Args:
            cyberdb: CyberDB instance to use. If None, creates from default config
            quiet: Whether to suppress output. If None, defaults to False
        """
        # FIXME: cyberdb is still not used, but will be to track history?
        if cyberdb is None:
            cyberdb = CyberDB.from_default_config()
        self.cyberdb = cyberdb

        self.quiet = quiet
        # Track times
        self._track_plugins_times: dict[str, dict[str, float]] = {}
        # Track exceptions
        self._plugins_exceptions: dict[str, dict[str, list]] = {}

        # Used when iterating plugins
        self._current_plugin = None
        self._current_plugin_manager = None
        # Boolean used to track if usage of context manager is correct or not
        self._is_iterating_plugins = False

        # Initialize Rich console once
        self._rich_console = get_rich_console()

    def iter_plugins(
        self,
        iterator=None,
        *,
        plugin_manager: PluginManager,
        plugins: Iterable[Plugin],
        iterator_description: str | Callable = None,
        iterator_total: int = None,
    ):
        """Utility function to iter plugins from a plugin manager with following features:
        - Track times spent by each plugins
        - Handle exceptions when using this class as context manager
        - Iter either plugins only, or an iterator in addition of the plugins
            (nested loop starting with iterator then plugins)

        Args:
            iterator: if provided will yield object_from_iterator, plugin else plugin only
            iterator_description: description in rich.progress, if callable
                will call it with each object from the iterable
        """
        # TODO: add granular history of running plugins

        # Set status to True when entering this function
        self._is_iterating_plugins = True
        self._current_plugin_manager = plugin_manager

        if iterator is not None and iterator_total is None:
            iterator_total = len(iterator)

        if iterator_description is None:
            iterator_description = "Processing..."

        # Get time tracker for current plugin
        if plugin_manager.name not in self._track_plugins_times:
            self._track_plugins_times[plugin_manager.name] = {}
        pm_time_track = self._track_plugins_times[plugin_manager.name]

        total_plugins = len(plugin_manager)

        # Use the instance console for progress
        with Progress(console=self._rich_console) as progress:
            if iterator:
                iterator_task = progress.add_task(
                    iterator_description, total=iterator_total
                )

            plugins_task = progress.add_task(
                f"Processing [cyan]'{plugin_manager.name}'[/cyan] plugins - (0/{total_plugins})",
                total=total_plugins,
            )

            if iterator is None:
                iterator = [Nothing]

            for iterator_e in iterator:
                if iterator_e is not Nothing:
                    if callable(iterator_description):
                        current_description = iterator_description(iterator_e)
                    else:
                        current_description = iterator_description

                    progress.update(
                        iterator_task,
                        advance=1,
                        description=current_description,
                    )

                for i_plugin, plugin in enumerate(plugins, start=1):
                    self._current_plugin = plugin
                    # time tracking
                    if plugin.name not in pm_time_track:
                        pm_time_track[plugin.name] = 0

                    # progress bar
                    progress.update(
                        plugins_task,
                        advance=1,
                        description=f"Processing [cyan]{plugin_manager.name}[/cyan] plugins : [cyan]{plugin.name}[/cyan] ({i_plugin}/{total_plugins})",
                    )

                    start_time = time.time()
                    if iterator_e is Nothing:
                        yield plugin
                    else:
                        yield plugin, iterator_e

                    # time tracking
                    end_time = time.time()
                    pm_time_track[plugin.name] += end_time - start_time

                progress.reset(plugins_task)
        self._is_iterating_plugins = False

    # TODO: add __enter__ as function and not ...
    @contextlib.contextmanager
    def handle_exceptions(self):
        # TODO: replace __enter__ here

        yield

    def __enter__(self):
        """Context manager used to silence and log exceptions"""
        if self._is_iterating_plugins is False:
            raise ValueError(
                "Using context manager is allowed only inside iter_plugins() method"
            )

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager used to silence and log exceptions"""
        if exc_type is not None:
            # Get current  pm & plugin
            pm_name = self._current_plugin_manager.name
            plugin_name = self._current_plugin.name

            # Init the nested dict structure of current pm/plugin
            if pm_name not in self._plugins_exceptions:
                self._plugins_exceptions[pm_name] = {}
            pm_errors = self._plugins_exceptions[pm_name]
            if plugin_name not in pm_errors:
                pm_errors[plugin_name] = []
            plugin_errors = pm_errors[plugin_name]

            # Add current exception
            plugin_errors.append((exc_type, exc_val, exc_tb))

            # Print only first 2 occurrences
            if len(plugin_errors) <= 2:
                self.print(
                    rf"[red]\[error][/red] exception occurred for {pm_name}.{plugin_name}: {exc_type.__name__} {exc_val}"
                )
                traceback.print_exception(exc_type, exc_val, exc_tb)

        return True  # Supress error

    def print(self, *args, **kwargs):
        """All prints goes from here, to have the possibility to silence it if needed"""
        if not self.quiet:
            # Use the instance console for consistent output
            self._rich_console.print(*args, **kwargs)

    def print_stats(self):
        self.print_time_tracking()
        self.print_errors()

    def print_time_tracking(self):
        sorted_pm_stats = sorted(
            self._track_plugins_times.items(),
            key=lambda pm: sum(pm[1].values()),
            reverse=True,
        )

        # Prepare and print statistics
        for pm_name, plugins in sorted_pm_stats:
            total_time = sum(plugins.values())
            self.print(f"\nPlugin Manager: {pm_name} (Total Time: {total_time:.2f}s)")

            # Sort plugins by their individual times
            sorted_plugins = sorted(
                plugins.items(), key=lambda plugin: plugin[1], reverse=True
            )
            for plugin_name, time_spent in sorted_plugins:
                self.print(f"  - Plugin: {plugin_name}, Time: {time_spent:.2f}s")
        self.print()

    def print_errors(self):
        sorted_pm_errors = sorted(
            self._plugins_exceptions.items(),
            key=lambda pm: sum(len(errors) for errors in pm[1].values()),
            reverse=True,
        )

        # Prepare and print total error count
        total_errors = sum(
            len(errors)
            for pm in self._plugins_exceptions.values()
            for errors in pm.values()
        )
        if total_errors:
            self.print(f"[red]{total_errors} errors occurred[/red]")

        # Iterate through sorted plugin managers
        for pm_name, pm_errors in sorted_pm_errors:
            total_errors_pm = sum(len(errors) for errors in pm_errors.values())
            self.print(f"  Plugins 'pm_name' (Total Errors: {total_errors_pm})")

            # Sort plugins by the number of errors
            sorted_plugins = sorted(
                pm_errors.items(), key=lambda plugin: len(plugin[1]), reverse=True
            )

            # Iterate through sorted plugins and print error counts
            for plugin_name, plugin_errors in sorted_plugins:
                unique_types = list({e[0].__name__ for e in plugin_errors})
                self.print(
                    f"    - {plugin_name}, Errors: {len(plugin_errors)} {unique_types}"
                )
