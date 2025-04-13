import itertools

import koalak
from cybsuite.cyberdb.cli.utils_cmd import CMD_GROUP_PLUGINS
from koalak.plugin_manager.packages_distributions_utils import (
    module_to_package_distribution_name,
)
from koalak.subcommand_parser import SubcommandParser


def add_cli_list(cli_main: SubcommandParser):
    cli_list = cli_main.add_subcommand(
        "list", group=CMD_GROUP_PLUGINS, description="List plugins"
    )
    cli_list.register_function(_run)


def _run(args):
    from cybsuite.cyberdb import pm_ingestors, pm_reporter

    plugins = itertools.chain(pm_ingestors, pm_reporter)
    rows = []
    for plugin in plugins:

        rows.append(
            {
                "type": plugin.metadata.plugin_manager.name,
                "name": plugin.name,
                "category": plugin.metadata.category,
                "description": plugin.metadata.description,
                "authors": "\n".join(plugin.metadata.authors),
                "distribution": module_to_package_distribution_name(plugin.__module__),
            }
        )
    koalak.containers.print_table(rows)
