import shutil
from pathlib import Path

from cybsuite.consts import (
    FOLDER_NAME_EXTRACTS,
    FOLDER_NAME_LOGS,
    FOLDER_NAME_REPORTS,
    FOLDER_NAME_REVIEW,
    FOLDER_NAME_UNARCHIVED,
    PATH_WORKSPACES,
)
from cybsuite.core.config import workspaces_config
from cybsuite.core.logger import get_logger

logger = get_logger()


def get_current_workspace_name() -> str:
    """Get the name of the default workspace.

    Returns:
        str: Name of the default workspace
    """
    return workspaces_config["current"]


def set_current_workspace(name: str) -> None:
    """Set the default workspace.

    Args:
        name: Name of the workspace to set as default

    Raises:
        FileNotFoundError: If workspace doesn't exist
    """
    from cybsuite.cyberdb.config import cyberdb_config

    # Verify workspace exists before setting as default
    get_workspace_path(name)
    workspaces_config["current"] = name

    new_cyberdb_name = "cyberdb_" + name
    cyberdb_config["name"] = new_cyberdb_name
    logger.info(f"Set cyberdb name to: '{new_cyberdb_name}'")


def create_workspace(
    name: str, *, force: bool | None = None, set_as_default: bool | None = None
) -> Path:
    """Create a new workspace with the required directory structure.

    Args:
        name: Name of the workspace to create
        force: If True, overwrite existing workspace. If None, defaults to False.
        set_as_default: If True, set as default workspace. If None, defaults to True.

    Returns:
        Path: Path to the created workspace

    Raises:
        FileExistsError: If workspace already exists and force=False
    """
    if force is None:
        force = False
    if set_as_default is None:
        set_as_default = True

    workspace_path = PATH_WORKSPACES / name

    # Check if workspace exists
    if workspace_path.exists():
        if force:
            shutil.rmtree(workspace_path)
        else:
            raise FileExistsError(
                f"Workspace '{name}' already exists at '{workspace_path}'"
            )

    # Create workspace structure
    directories = [
        workspace_path,
        workspace_path / FOLDER_NAME_REVIEW / FOLDER_NAME_EXTRACTS,
        workspace_path / FOLDER_NAME_REVIEW / FOLDER_NAME_REPORTS,
        workspace_path / FOLDER_NAME_REVIEW / FOLDER_NAME_LOGS,
        workspace_path / FOLDER_NAME_REVIEW / FOLDER_NAME_UNARCHIVED,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=force)

    if set_as_default:
        set_current_workspace(name)

    return workspace_path


def list_workspaces_names() -> list[str]:
    """List all available workspaces.

    Returns:
        list[str]: List of workspace names
    """
    if not PATH_WORKSPACES.exists():
        return []

    return [d.name for d in PATH_WORKSPACES.iterdir() if d.is_dir()]


def get_workspace_path(name: str) -> Path:
    """Get the path to a specific workspace.

    Args:
        name: Name of the workspace

    Returns:
        Path: Path to the workspace

    """
    workspace_path = PATH_WORKSPACES / name
    return workspace_path


def get_current_workspace_path() -> Path:
    """Get the path to the current workspace.

    Returns:
        Path: Path to the current workspace
    """
    return get_workspace_path(get_current_workspace_name())


def delete_workspace(name: str) -> None:
    """Delete a workspace.

    Args:
        name: Name of the workspace to delete

    Raises:
        FileNotFoundError: If workspace doesn't exist
    """
    workspace_path = get_workspace_path(name)
    shutil.rmtree(workspace_path)
