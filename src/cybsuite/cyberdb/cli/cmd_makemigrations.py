from koalak.subcommand_parser import SubcommandParser

from .. import CyberDB
from .utils_cmd import CMD_GROUP_MIGRATIONS


def add_cli_makemigrations(cli_main: SubcommandParser):
    cli_subcmd = cli_main.add_subcommand(
        "makemigrations",
        group=CMD_GROUP_MIGRATIONS,
        description="Make migrations for Database",
    )
    cli_subcmd.register_function(_run)


def _run(args):
    CyberDB.makemigrations()
