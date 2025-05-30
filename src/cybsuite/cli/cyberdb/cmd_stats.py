from cybsuite.core.logger import get_logger
from cybsuite.cyberdb import CyberDB, cyberdb_schema
from koalak.subcommand_parser import SubcommandParser
from rich.console import Console
from rich.table import Table

from .utils_cmd import CMD_GROUP_UTILS

logger = get_logger()
console = Console()


def add_cli_stats(cli_main: SubcommandParser):
    subcmd = cli_main.add_subcommand(
        "stats",
        group=CMD_GROUP_UTILS,
        description="Display row counts for each non-empty table in the database",
    )

    subcmd.register_function(_run)


def _run(args):
    cyberdb = CyberDB.from_default_config()

    table = Table(title="Database Statistics")
    table.add_column("Table Name", style="cyan")
    table.add_column("Row Count", justify="right", style="green")

    has_data = False

    for entity in cyberdb_schema:
        count = cyberdb.count(entity.name)
        if count > 0:
            has_data = True
            table.add_row(entity.name, str(count))

    if has_data:
        console.print(table)
    else:
        console.print("[yellow]No data found in any tables[/yellow]")
