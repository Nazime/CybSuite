import os
import traceback
from pathlib import Path

from koalak.subcommand_parser import SubcommandParser


def subcommand_add_plugins_filters_arguments(cmd: SubcommandParser):
    cmd.add_group("filter_plugins", title="Plugins filters")
    for filter_name in [
        "name",
        "category",
        "sub-category",
        "tags",
        "authors",
        "controls",
    ]:
        cmd.add_argument(
            f"--{filter_name}",
            group="filter_plugins",
            nargs="+",
            help=f"Filter by {filter_name}",
        )


def cmd_add_targets_arguments(cmd):
    cmd.add_argument(
        "targets",
        nargs="+",
        help="List of targets. Format: <ip> or <starting_ip>~<ending_ip> or <network>",
    )
    cmd.add_argument(
        "--exclude",
        nargs="+",
        help="List of targets to exclude. Format: <ip> or <starting_ip>~<ending_ip> or <network>",
    )
    cmd.add_argument(
        "-p",
        "--ports",
        nargs="+",
        help="List of ports. Format: <port> or <starting_port>-<ending_port>",
    )
    cmd.add_argument(
        "--node",
        help="Specify the current node and the number of nodes, "
        "it's useful to run the same scan accros several machines. Format <id_node>/<nb_node>",
    )


def log_exception(exception: Exception, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as log_file:
        log_file.write(f"Exception: {str(exception)}\n")
        log_file.write(traceback.format_exc() + "\n\n--------\n\n")


def is_root():
    """Return True if this proces is executed in root"""
    return os.getuid() == 0
