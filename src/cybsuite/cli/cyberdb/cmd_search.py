from cybsuite.core.logger import get_logger
from cybsuite.cyberdb import CyberDB
from koalak.subcommand_parser import SubcommandParser
from rich.console import Console

from .utils_cmd import CMD_GROUP_UTILS

logger = get_logger()
console = Console()


def add_cli_search(cli_main: SubcommandParser):
    subcmd = cli_main.add_subcommand(
        "search",
        group=CMD_GROUP_UTILS,
        description="[Work In Progress] Search records in a specified table",
    )

    subcmd.add_argument("table_name", help="Name of the table to search in")
    subcmd.register_function(_run)


def _run(args):
    cyberdb = CyberDB.from_default_config()
    # TODO: Implement search functionality
    console.print(
        f"[yellow]Search functionality for table '{args.table_name}' will be implemented soon[/yellow]"
    )
