import argparse

import koalak
from cybsuite.cyberdb import CyberDB, pm_reporters
from koalak.subcommand_parser import SubcommandParser

from .utils_cmd import CMD_GROUP_PLUGINS, print_reporters_table


class ListAndExit(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print_reporters_table()
        parser.exit()


def add_cli_report(cli_main: SubcommandParser):
    subcmd = cli_main.add_subcommand(
        "report", group=CMD_GROUP_PLUGINS, description="Generate report"
    )
    subcmd.add_argument(
        "--list",
        action=ListAndExit,
        help="List all available reporters and exit",
        nargs=0,
    )
    subcmd.add_argument("type", choices=[e.name for e in pm_reporters])
    subcmd.add_argument("output")
    subcmd.register_function(_run)


def _run(args):
    type = args.type
    output = args.output

    cls_reporter = pm_reporters[type]
    db = CyberDB.from_default_config()
    reporter = cls_reporter(db)
    reporter.run(output)
