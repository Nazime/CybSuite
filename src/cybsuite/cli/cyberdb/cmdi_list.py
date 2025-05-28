import itertools

import koalak
from cybsuite.cyberdb import (
    pm_formatters,
    pm_ingestors,
    pm_passive_scanners,
    pm_reporters,
)
from koalak.subcommand_parser import SubcommandParser

from .utils_cmd import (
    CMD_GROUP_PLUGINS,
    print_formatters_table,
    print_ingestors_table,
    print_reporters_table,
    print_scanners_table,
)

plugin_managers = {
    pm_ingestors.name: pm_ingestors,
    pm_reporters.name: pm_reporters,
    pm_passive_scanners.name: pm_passive_scanners,
    pm_formatters.name: pm_formatters,
}


def add_cli_list(cli_main: SubcommandParser):

    cli_list = cli_main.add_subcommand(
        "list", group=CMD_GROUP_PLUGINS, description="List plugins"
    )
    cli_list.add_argument(
        "type",
        nargs="?",
        choices=list(plugin_managers.keys()),
        help="Filter plugins by type and show detailed information",
    )
    cli_list.register_function(_run)


def _run(args):

    COLOR_MAP = {
        pm_ingestors.name: "green",
        pm_reporters.name: "blue",
        pm_passive_scanners.name: "magenta",
        pm_formatters.name: "yellow",
    }

    rows = []

    if args.type:

        if args.type == pm_ingestors.name:
            print_ingestors_table()
        elif args.type == pm_reporters.name:
            print_reporters_table()
        elif args.type == pm_passive_scanners.name:
            print_scanners_table()
        elif args.type == pm_formatters.name:
            print_formatters_table()

    else:
        # Overview of all plugins
        plugins = itertools.chain(*plugin_managers.values())
        for plugin in plugins:
            plugin_type = plugin.metadata.plugin_manager.name
            color = COLOR_MAP[plugin_type]
            rows.append(
                {
                    "type": f"[{color}]{plugin_type}[/]",
                    "name": plugin.name,
                    "description": plugin.metadata.description,
                }
            )

    koalak.containers.print_table(rows)
