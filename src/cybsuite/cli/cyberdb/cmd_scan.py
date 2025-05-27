from cybsuite.cyberdb import CyberDB, pm_passive_scanners
from koalak.subcommand_parser import SubcommandParser

from .utils_cmd import CMD_GROUP_PLUGINS


def add_cli_scan(cli_main: SubcommandParser):
    subcmd = cli_main.add_subcommand(
        "scan", group=CMD_GROUP_PLUGINS, description="Passively scan database"
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
