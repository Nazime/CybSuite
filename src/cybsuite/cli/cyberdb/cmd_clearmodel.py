import rich
from cybsuite.cyberdb import CyberDB
from koalak.subcommand_parser import SubcommandParser
from rich.prompt import Confirm

from .utils_cmd import CMD_GROUP_DELETE


def add_cli_clearmodel(cli_main: SubcommandParser):
    cli_clearmodel = cli_main.add_subcommand(
        "clearmodel",
        description="Clear all data of a specific model (DANGEROUS)",
        group=CMD_GROUP_DELETE,
    )
    cli_clearmodel.add_argument(
        "model_name",
        help="Name of the model to clear",
    )
    cli_clearmodel.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompt",
    )
    cli_clearmodel.register_function(_run)


def _run(args):
    if not args.force:
        if not Confirm.ask(
            f"[red]WARNING[/red]: This will delete all data in the {args.model_name} model. Are you sure?",
            default=False,
        ):
            print("Operation cancelled.")
            return

    cyberdb = CyberDB.from_default_config()
    cyberdb.clear_one_model(args.model_name)
    rich.print(f"[green]Model {args.model_name} cleared successfully[/green]")
