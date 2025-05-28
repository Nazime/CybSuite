import rich
from cybsuite.cyberdb import CyberDB
from koalak.subcommand_parser import SubcommandParser
from rich.prompt import Confirm

from .utils_cmd import CMD_GROUP_DELETE


def add_cli_cleardb(cli_main: SubcommandParser):
    cli_cleardb = cli_main.add_subcommand(
        "cleardb",
        description="Clear all data of all models (DANGEROUS)",
        group=CMD_GROUP_DELETE,
    )
    cli_cleardb.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompt",
    )
    cli_cleardb.register_function(_run)


def _run(args):
    if not args.force:
        if not Confirm.ask(
            "[red]WARNING[/red]: This will delete all data in the database. Are you sure?",
            default=False,
        ):
            print("Operation cancelled.")
            return

    cyberdb = CyberDB.from_default_config()
    cyberdb.cleardb()
    rich.print("[green]Database cleared successfully[/green]")
