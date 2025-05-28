"""Command to add files to the workspace extracts directory."""

import shutil
from pathlib import Path

from cybsuite.consts import FOLDER_NAME_EXTRACTS, FOLDER_NAME_REVIEW
from cybsuite.workspace.workspaces import get_current_workspace_path
from koalak.subcommand_parser import SubcommandParser


def add_cmd_add(cmd_main: SubcommandParser):
    """Add the add command to the main CLI."""
    subcmd = cmd_main.add_subcommand(
        "add", description="Add files to the current workspace extracts directory"
    )
    subcmd.add_argument(
        "filepaths",
        nargs="+",
        help="One or more paths to files to add to current workspace",
    )
    subcmd.add_argument(
        "--move",
        action="store_true",
        help="Move the file instead of copying it (useful for large files)",
    )
    subcmd.register_function(_run)


def _run(args):
    try:
        # Get the current workspace
        workspace_path = get_current_workspace_path()

        # Get the extracts directory
        extracts_dir = workspace_path / FOLDER_NAME_REVIEW / FOLDER_NAME_EXTRACTS
        if not extracts_dir.exists():
            extracts_dir.mkdir(parents=True)

        # Process each file
        for filepath in args.filepaths:
            source_path = Path(filepath)
            if not source_path.exists():
                print(f"Error: File '{source_path}' does not exist")
                continue

            dest_path = extracts_dir / source_path.name

            # Move or copy the file based on the --move option
            if args.move:
                shutil.move(source_path, dest_path)
                action = "Moved"
            else:
                shutil.copy2(source_path, dest_path)
                action = "Added"

            print(f"{action} '{source_path.name}' to {extracts_dir}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: Failed to add files - {e}")
