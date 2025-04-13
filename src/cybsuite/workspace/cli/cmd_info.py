"""Command to show workspace information."""

from cybsuite.consts import FOLDER_NAME_UNARCHIVED
from cybsuite.cyberdb.config import cyberdb_config
from cybsuite.workspace.workspaces import (
    get_current_workspace_name,
    get_workspace_path,
    list_workspaces_names,
)
from koalak.subcommand_parser import SubcommandParser
from rich.console import Console
from rich.panel import Panel
from rich.style import Style
from rich.text import Text


def add_cmd_info(cmd_workspace: SubcommandParser):
    """Add the info command to show workspace information."""
    subcmd = cmd_workspace.add_subcommand(
        "info", description="Show workspace information"
    )
    subcmd.register_function(_run)


def _run(args):
    console = Console()

    current_workspace = get_current_workspace_name()
    current_workspace_path = get_workspace_path(current_workspace)
    workspaces = list_workspaces_names()

    # Create current workspace info panel
    info_text = Text()

    # Path info
    info_text.append("Workspace Path: ", style="yellow")
    info_text.append(str(current_workspace_path), style="cyan")
    info_text.append("\n")

    # Database info
    info_text.append("Database: ", style="yellow")
    info_text.append(f"{cyberdb_config['name']}", style="cyan")
    info_text.append(" at ", style="dim")
    info_text.append(f"{cyberdb_config['user']}", style="green")
    info_text.append("@", style="dim")
    info_text.append(f"{cyberdb_config['host']}", style="blue")
    info_text.append(":", style="dim")
    info_text.append(f"{cyberdb_config['port']}\n", style="magenta")

    # Extracts info
    info_text.append("Extracts: ", style="yellow")
    extracts_dir = current_workspace_path / FOLDER_NAME_UNARCHIVED

    if not extracts_dir.exists():
        info_text.append("(directory not created yet)", style="dim italic")
    else:
        files = sorted(extracts_dir.iterdir())
        if not files:
            info_text.append("(empty)", style="dim italic")
        else:
            for file_path in files:
                size = file_path.stat().st_size
                size_str = f"{size:,} bytes"
                info_text.append(f"\n  {file_path.name}", style="cyan")
                info_text.append(f" ({size_str})", style="dim")

    info_panel = Panel(
        info_text,
        title=f"[yellow]Current Workspace [cyan]'{current_workspace}'[/cyan][/yellow]",
        border_style="blue",
    )
    console.print(info_panel)
    console.print()

    # Create workspaces panel
    workspaces_text = Text()
    workspaces_list = sorted(workspaces)

    # Add each workspace to the text, with newlines between entries but not at the end
    for i, workspace in enumerate(workspaces_list):
        # Add the workspace entry with appropriate styling
        if workspace == current_workspace:
            workspaces_text.append(f"→ {workspace} (current)", style="green bold")
        else:
            workspaces_text.append(f"  {workspace}", style="dim")

        # Add a newline after each entry except the last one
        if i < len(workspaces_list) - 1:
            workspaces_text.append("\n")

    workspaces_panel = Panel(
        workspaces_text,
        title="[yellow]Available Workspaces[/yellow]",
        border_style="blue",
    )
    console.print(workspaces_panel)
