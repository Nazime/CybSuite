"""
TODO: Many sub commands and code are not used. Will be added or removed in future versions!"""
import sys

import rich
from cybsuite.cyberdb import CyberDB, pm_ingestors, pm_reporter
from cybsuite.cyberdb.config import cyberdb_config
from koalak.subcommand_parser import SubcommandParser
from rich.console import Console

from .cmd_ingest import add_cli_ingest
from .cmd_makemigrations import add_cli_makemigrations
from .cmd_migrate import add_cli_migrate
from .cmd_report import add_cli_report
from .cmd_scan import add_cli_scan
from .cmd_schema import add_cli_schema
from .cmdi_list import add_cli_list
from .utils_cmd import (
    CMD_GROUP_MIGRATIONS,
    CMD_GROUP_OTHERS,
    CMD_GROUP_PLUGINS,
    CMD_GROUP_UTILS,
)

console = Console()


def build_command(main_command: SubcommandParser = None):
    # TODO: check if it is necessary to intiantiate it here!
    cyberdb = CyberDB.from_default_config()
    if main_command is None:

        main_cli = SubcommandParser("cyberdb", description="Manage the database")
    else:
        main_cli = main_command.add_subcommand(
            "cyberdb", description="Manage the database (same as cmd cyberdb)"
        )

    # Creating CMD groups #
    main_cli.add_group(name=CMD_GROUP_PLUGINS, title="Plugins & Features")
    group_database_operations = main_cli.add_group(title="Database operations")
    main_cli.add_group(name=CMD_GROUP_UTILS, title="Utils functions")

    group_delete = main_cli.add_group(title="Database delete operations")
    main_cli.add_group(
        name=CMD_GROUP_MIGRATIONS,
        title="Migrations",
        description="Mainly used for development",
    )

    main_cli.add_group(name=CMD_GROUP_OTHERS, title="Others")

    cmd_request = main_cli.add_subcommand(
        "request",
        description="Request data from a specific model",
        group=group_database_operations.name,
    )

    cmd_feed = main_cli.add_subcommand(
        "feed",
        description="upsert (insert or update) new entry",
        group=group_database_operations.name,
    )

    # Group plugins
    add_cli_list(main_cli)
    add_cli_ingest(main_cli)
    add_cli_scan(main_cli)
    add_cli_report(main_cli)

    # Groups migrations
    add_cli_makemigrations(main_cli)
    add_cli_migrate(main_cli)

    # Other
    add_cli_schema(main_cli)

    main_cli.add_subcommand_from_function(
        CyberDB.resolve_ip,
        default_instance=cyberdb,
        group=CMD_GROUP_UTILS,
    )

    cmd_count = main_cli.add_subcommand("count", group=group_database_operations.name)
    cmd_count.add_argument("model_name")
    cmd_count.register_function(run_count)

    main_cli.add_subcommand_from_function(
        CyberDB.cleardb,
        default_instance=cyberdb,
        group=group_delete.name,
        description="Clear all data of all models",
    )

    # Imports & Exports CLIs #
    # ====================== #

    for entity in CyberDB.schema:
        # Dynamically build the parser 'request' based on registered requests in the Requestor cls
        cmd_request_entity = cmd_request.add_subcommand(
            entity.name, description=entity.description
        )
        group_filters = cmd_request_entity.add_group(title="Filters")
        group_negative_filters = cmd_request_entity.add_group(title="Negative filters")
        group_general = cmd_request_entity.add_group(title="General Options")
        # Adding matching arguments dynamically based on consts description
        cmd_request_entity.add_argument("--entity-name", hide=True, default=entity.name)
        for attribute in entity:
            attribute_type = attribute.type
            # For the moment only add str and int attributes for filters (ignore list and dict)
            if attribute_type is str or attribute_type is int:
                cmd_request_entity.add_argument(
                    f"--{attribute.name}",
                    type=attribute_type,
                    group=group_filters,
                )
                cmd_request_entity.add_argument(
                    f"--no-{attribute.name}",
                    type=attribute_type,
                    nargs="+",
                    group=group_negative_filters,
                )
            elif False:  # FIXME
                # elif attribute_type == Set[str]:
                cmd_request_entity.add_argument(
                    f"--{attribute.name}",
                    type=str,
                    nargs="+",
                    group=group_filters,
                )
                cmd_request_entity.add_argument(
                    f"--no-{attribute.name}",
                    type=str,
                    nargs="+",
                    group=group_negative_filters,
                )

        # Add common arguments
        cmd_request_entity.add_argument(
            "--sort",
            help="Sort",
            type=str,
            nargs="+",
            group=group_general,
        )
        cmd_request_entity.add_argument(
            "--limit",
            help="Limit to n results",
            type=int,
            group=group_general,
        )
        cmd_request_entity.add_argument(
            "--skip",
            help="Skip the n first results",
            type=int,
            group=group_general,
        )
        cmd_request_entity.add_argument(
            "--fields",
            help="Fields to show",
            type=str,
            nargs="+",
            group=group_general,
        )
        cmd_request_entity.add_argument(
            "--no-fields",
            help="Fields to hide",
            type=str,
            nargs="+",
            group=group_general,
        )
        cmd_request_entity.add_argument(
            "--format",
            help="Format of resulting query",
            choices=["humain", "csv", "xlsx"],
            default="human",
            group=group_general,
        )
        cmd_request_entity.add_argument(
            "-o",
            "--output",
            help="Output file, default to stdout",
            group=group_general,
        )
        cmd_request_entity.add_argument(
            "-c",
            "--count",
            help="Count the number of entries",
            action="store_true",
            group=group_general,
        )
        cmd_request_entity.register_function(run_request)

    for entity in CyberDB.schema:
        # Dynamically build the parser 'feed' based on registered requests in the Requestor cls

        cmd_feed_entity = cmd_feed.add_subcommand(entity.name)
        cmd_feed_entity.add_argument("--entity_name", hide=True, default=entity.name)

        # Adding matching arguments dynamically based on consts description
        for field in entity:
            # For the moment only add str and int attributes for filters (ignore list and dict)
            if field.type is str or field.type is int:
                if field.required:
                    name = field.name
                else:
                    name = f"--{field.name}"
                cmd_feed_entity.add_argument(name, type=field.type)
        cmd_feed_entity.register_function(run_feed)

    return main_cli


def print_and_exit(*msg):
    rich.print("[red]ERROR[/red]", *msg)
    sys.exit(1)


def print_success(*msg):
    rich.print("[green]\\[+][/green]", *msg)


# ################### #
# DB RELATED COMMANDS #
# ################### #


def run_request(args):
    db = CyberDB.from_default_config()
    for e in db.request(args.entity_name):
        print(e)


def run_count(args):
    name = args.model_name
    cyberdb = CyberDB.from_default_config()
    print(cyberdb.count(name))


# =========== #
# FEED PARSER #
# =========== #
def run_feed(args):
    db = CyberDB.from_default_config()
    args = vars(args)
    entity_name = args.pop("entity_name")
    result = db.feed(entity_name, **args)
    print(result)


def main():
    cmd_ssdb = build_command()
    cmd_ssdb.run()


if __name__ == "__main__":
    main()
