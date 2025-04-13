"""Installation logic for CybSuite. This is the FIRST module to be executed when importing cybsuite."""

from ..consts import CONF_FILE_NAME, PATH_CYBSUITE, PATH_WORKSPACES
from .logger import get_logger, get_rich_console

logger = get_logger()


def is_installed() -> bool:
    """Check if CybSuite is already installed.

    Returns:
        bool: True if CybSuite is installed, False otherwise
    """
    return PATH_CYBSUITE.exists()


def install():
    """Install CybSuite by creating necessary directories and files."""
    # Check if already installed
    if is_installed():
        logger.debug("CybSuite is already installed!")
        return

    console = get_rich_console()
    # First time installation
    logger.info("First time use detected")

    # Create main directory
    logger.info(f"Creating home directory structure '{PATH_CYBSUITE}'")
    PATH_CYBSUITE.mkdir(parents=True, exist_ok=True)

    # Create config file
    from .config import root_config

    logger.info(f"Creating main config file '{CONF_FILE_NAME}'")

    # Create workspace directory
    from cybsuite.workspace.workspaces import (
        create_workspace,
        get_current_workspace_name,
        get_current_workspace_path,
    )

    current_workspace_name = get_current_workspace_name()
    current_workspace_path = get_current_workspace_path()
    logger.info(
        f"Creating '{current_workspace_name}' workspace in '{current_workspace_path}'"
    )
    PATH_WORKSPACES.mkdir(parents=True, exist_ok=True)
    create_workspace(current_workspace_name)

    console.print()
