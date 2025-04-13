import logging
import sys
from pathlib import Path

from cybsuite.consts import LOGGER_NAME
from rich.console import Console
from rich.logging import RichHandler

_logger = None
_console = None


def is_running_from_cli():
    filename = Path(sys.argv[0]).name
    if filename.startswith("cybs-") or filename.startswith("cybsuite"):
        return True
    return False


def get_rich_console():
    """Get a singleton instance of Rich console.

    Returns:
        A Rich console instance that can be used for consistent output formatting.
    """
    global _console
    if _console is None:
        _console = Console()
    return _console


def get_logger():
    global _logger
    if _logger is not None:
        return _logger

    if is_running_from_cli():
        logging_level = logging.INFO
    else:
        logging_level = logging.CRITICAL + 1

    # Create logger
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging_level)

    # Create Rich handler with the shared console and custom format
    rich_handler = RichHandler(
        console=get_rich_console(),
        show_path=False,  # Don't show the file path
        show_time=False,  # Don't show the time
        rich_tracebacks=True,  # Keep rich tracebacks
        markup=True,  # Keep markup
        show_level=True,  # Keep the log level
    )
    logger.addHandler(rich_handler)

    _logger = logger
    return _logger


def set_log_level(level: int):
    """Set the log level for both logger and its handlers.

    Args:
        level: The logging level to set (e.g. logging.DEBUG, logging.INFO)
    """
    logger = get_logger()
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)
