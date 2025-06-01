import argparse

import koalak
from cybsuite.cyberdb import CyberDB, pm_passive_scanners
from koalak.subcommand_parser import SubcommandParser

from .utils_cmd import CMD_GROUP_PLUGINS, print_scanners_table


class ListAndExit(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print_scanners_table()
        parser.exit()


def add_cli_scan(cli_main: SubcommandParser):
    subcmd = cli_main.add_subcommand(
        "scan",
        group=CMD_GROUP_PLUGINS,
        description="Run passive scanners to identify vulnerabilities and update the database (add/modify/remove entries)",
    )
    subcmd.add_argument(
        "--list",
        action=ListAndExit,
        help="List all available scanners and exit",
        nargs=0,
    )
    subcmd.add_argument(
        "name",
        help="Name of the tool",
        choices=["all"] + list(e.name for e in pm_passive_scanners),
    )
    subcmd.register_function(_run)


def _run(args):
    db = CyberDB.from_default_config()
    db.scan(args.name)
