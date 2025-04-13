"""Command to switch between workspaces."""

from cybsuite.core.logger import get_logger
from cybsuite.workspace.workspaces import (
    get_current_workspace_name,
    get_workspace_path,
    list_workspaces_names,
    set_current_workspace,
)
from koalak.subcommand_parser import SubcommandParser

logger = get_logger()


def add_cmd_switch(cmd_workspace: SubcommandParser):
    """Add the switch command to the workspace subcommand."""
    subcmd = cmd_workspace.add_subcommand(
        "switch", description="Switch to a different workspace"
    )
    subcmd.add_argument("name", help="Name of the workspace to switch to")
    subcmd.register_function(_run)


def _run(args):
    try:
        # Check if workspace exists
        if args.name not in list_workspaces_names():
            logger.error(f"Workspace '{args.name}' not found")
            return

        # Get current workspace before switching
        current_workspace = get_current_workspace_name()

        # Check if already in the requested workspace
        if current_workspace == args.name:
            logger.info(f"Already in workspace '{args.name}'")
            return

        current_workspace_path = get_workspace_path(current_workspace)

        # Switch to the new workspace
        set_current_workspace(args.name)
        new_workspace_path = get_workspace_path(args.name)

        # Log the switch
        logger.info(f"Switched from workspace '{current_workspace}' to '{args.name}'")
        logger.info(f"Current workspace path: '{new_workspace_path}'")

    except Exception as e:
        logger.error(f"Failed to switch workspace: {e}")
