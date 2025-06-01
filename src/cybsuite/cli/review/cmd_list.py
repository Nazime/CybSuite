import itertools

import koalak.containers
from cybsuite.review.windows import pm_reviewers
from cybsuite.utils import subcommand_add_plugins_filters_arguments
from koalak.subcommand_parser import SubcommandParser


def add_cmd_list(cmd_main: SubcommandParser):
    subcmd = cmd_main.add_subcommand(
        "list",
        description="List and filter available CybSuite review plugins with detailed information",
    )
    subcommand_add_plugins_filters_arguments(subcmd)
    subcmd.register_function(_run)


def _run(args):
    plugins = itertools.chain(pm_reviewers)
    rows = []
    for plugin in plugins:
        rows.append(
            {
                "type": plugin.metadata.plugin_manager.name,
                "name": plugin.name,
                "category": plugin.metadata.category,
                "description": plugin.metadata.description,
                "controls": "\n".join(plugin.controls),
                "authors": "\n".join(plugin.metadata.authors),
            }
        )
    koalak.containers.print_table(rows)
