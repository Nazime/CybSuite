import itertools

import koalak
from koalak.subcommand_parser import SubcommandParser

from .utils_cmd import CMD_GROUP_PLUGINS


def add_cli_list(cli_main: SubcommandParser):
    cli_list = cli_main.add_subcommand(
        "list", group=CMD_GROUP_PLUGINS, description="List plugins"
    )
    cli_list.register_function(_run)


def _run(args):
    from cybsuite.cyberdb import (
        pm_formatters,
        pm_ingestors,
        pm_passive_scanners,
        pm_reporters,
    )

    plugins = itertools.chain(
        pm_ingestors, pm_reporters, pm_passive_scanners, pm_formatters
    )
    rows = []
    for plugin in plugins:

        rows.append(
            {
                "type": plugin.metadata.plugin_manager.name,
                "name": plugin.name,
                # "category": plugin.metadata.category,
                "description": plugin.metadata.description,
                # "authors": "\n".join(plugin.metadata.authors),
                # "distribution": module_to_package_distribution_name(plugin.__module__),
            }
        )
    koalak.containers.print_table(rows)
