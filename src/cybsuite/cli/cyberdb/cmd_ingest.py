import argparse
import sys

import koalak
from cybsuite.cyberdb import CyberDB, pm_ingestors
from koalak.subcommand_parser import SubcommandParser

from .utils_cmd import CMD_GROUP_PLUGINS, print_ingestors_table


class ListAndExit(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print_ingestors_table()
        parser.exit()


def add_cli_ingest(cli_main: SubcommandParser):
    subcmd = cli_main.add_subcommand(
        "ingest",
        group=CMD_GROUP_PLUGINS,
        description="Import data from known tools (ex: nmap)",
    )
    help_ingest_cli = """
       Import results of a given tool to the pentestdb database:
       You can recursively import a folder with `pentestdb ingest all <path_folder>`, the selected ingestor is based on the file extension:
       """
    for ingestor in pm_ingestors:
        help_ingest_cli += f"  {ingestor.name.ljust(10)}: {ingestor.extension!r}\n"

    subcmd.add_argument(
        "--list",
        action=ListAndExit,
        help="List all available ingestors and exit",
        nargs=0,
    )

    subcmd.add_argument(
        "ingestor_name",
        help="Name of the tool",
        choices=["all"] + list(e.name for e in pm_ingestors),
    )

    subcmd.add_argument("filepaths", help="files to import", nargs="+")
    subcmd.register_function(_run)


def _run(args):
    ingestor_name = args.ingestor_name
    filepaths = args.filepaths
    cyberdb = CyberDB.from_default_config()
    cyberdb.ingest(ingestor_name, filepaths)
