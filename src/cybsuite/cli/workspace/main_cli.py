"""Main CLI setup for workspace management."""

import logging

from cybsuite.core.logger import get_logger
from koalak.subcommand_parser import SubcommandParser

from .cmd_create import add_cmd_create
from .cmd_delete import add_cmd_delete
from .cmd_info import add_cmd_info
from .cmd_switch import add_cmd_switch

cmd_main = SubcommandParser(
    "cybs-workspace", description="CybSuite Workspace Management"
)

add_cmd_info(cmd_main)
add_cmd_create(cmd_main)
add_cmd_switch(cmd_main)
add_cmd_delete(cmd_main)


def main():
    # Run the CLI
    cmd_main.run()


if __name__ == "__main__":
    main()
