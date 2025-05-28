"""Command to delete a workspace."""

from cybsuite.core.logger import get_logger
from cybsuite.workspace.workspaces import delete_workspace, get_current_workspace_name
from koalak.subcommand_parser import SubcommandParser

logger = get_logger()


def add_cmd_delete(cmd_workspace: SubcommandParser):
    """Add the delete command to the workspace subcommand."""
    subcmd = cmd_workspace.add_subcommand(
        "delete", description="Delete a workspace (requires --force flag)"
    )
    subcmd.add_argument("name", help="Name of the workspace to delete")
    subcmd.add_argument(
        "--force",
        action="store_true",
        help="Required flag to confirm workspace deletion",
    )
    subcmd.register_function(_run)


def _run(args):
    if not args.force:
        logger.error("'--force' flag is required for workspace deletion")
        logger.error("This is a safety measure to prevent accidental deletions")
        return

    try:
        delete_workspace(args.name)
        logger.info(f"Deleted workspace: '{args.name}'")

    except FileNotFoundError as e:
        logger.error(f"Workspace '{args.name}' not found")
    except Exception as e:
        logger.error(f"Failed to delete workspace - '{args.name}': {e}")
