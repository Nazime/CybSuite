"""Command to create new workspaces."""

from cybsuite.core.logger import get_logger
from cybsuite.workspace.workspaces import create_workspace, get_current_workspace_name
from koalak.subcommand_parser import SubcommandParser

logger = get_logger()


def add_cmd_create(cmd_workspace: SubcommandParser):
    """Add the create command to the workspace subcommand."""
    subcmd = cmd_workspace.add_subcommand(
        "create", description="Create a new workspace for security assessment"
    )
    subcmd.add_argument("name", help="Name of the workspace to create")
    subcmd.add_argument(
        "--force", action="store_true", help="Overwrite existing workspace if it exists"
    )
    subcmd.add_argument(
        "--no-default", action="store_true", help="Don't set as default workspace"
    )
    subcmd.register_function(_run)


def _run(args):
    try:
        workspace_path = create_workspace(
            args.name, force=args.force, set_as_default=not args.no_default
        )
        logger.info(f"Created new workspace at: '{workspace_path}'")

        # Always show the current default workspace
        default_workspace = get_current_workspace_name()
        logger.info(f"Set it as current workspace: '{default_workspace}'")
    except FileExistsError as e:
        logger.error(f"{e}")
        logger.error("Use '--force' to overwrite existing workspace")
