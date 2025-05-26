from cybsuite.cyberdb import CyberDB
from koalak.subcommand_parser import SubcommandParser

from .utils_cmd import CMD_GROUP_MIGRATIONS


def add_cli_migrate(cli_main: SubcommandParser):
    cli_subcmd = cli_main.add_subcommand(
        "migrate",
        group=CMD_GROUP_MIGRATIONS,
        description="Migrate database (after update leading to DB schema changes)",
    )
    cli_subcmd.register_function(_run)


def _run(args):
    cyberdb = CyberDB.from_default_config()
    cyberdb.migrate()
