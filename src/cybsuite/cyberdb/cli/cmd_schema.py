from cybsuite.core.logger import get_logger
from cybsuite.cyberdb import cyberdb_schema
from cybsuite.cyberdb.cli.utils_cmd import CMD_GROUP_OTHERS
from koalak.subcommand_parser import SubcommandParser

logger = get_logger()


def add_cli_schema(cli_main: SubcommandParser):
    subcmd = cli_main.add_subcommand(
        "schema",
        group=CMD_GROUP_OTHERS,
        description="Describe the the schema of CyberDB",
    )

    subcmd.add_argument(
        "--list",
        action="store_true",
        help="Only list the names of entities without printing full details",
    )

    subcmd.add_argument(
        "entities",
        nargs="*",
        help="Specific entity names to describe. If not provided, describes all entities.",
        # TODO: choices is breaking things
        # choices=list(e.name for e in cyberdb_schema),
    )

    subcmd.register_function(_run)


def _run(args):
    if args.list:
        for entity in sorted(cyberdb_schema, key=lambda x: x.name):
            print(entity.name)
        return

    if not args.entities:
        entities = [entity.name for entity in cyberdb_schema]
    else:
        list_not_found = []
        for entity_name in args.entities:
            if entity_name not in cyberdb_schema:
                list_not_found.append(entity_name)
        if list_not_found:
            logger.error(f"Entities not found: {', '.join(list_not_found)}")
            return
        entities = args.entities

    for entity_name in sorted(entities):
        cyberdb_schema[entity_name].rich_print()
