from cybsuite.cyberdb import CyberDB, pm_ingestors
from cybsuite.cyberdb.cli.utils_cmd import CMD_GROUP_PLUGINS
from koalak.subcommand_parser import SubcommandParser


def add_cli_scan(cli_main: SubcommandParser):
    subcmd = cli_main.add_subcommand(
        "scan", group=CMD_GROUP_PLUGINS, description="Passively scan database"
    )
    subcmd.add_argument("dbname")
    subcmd.register_function(_run)


def _run(args):
    db = CyberDB.from_default_config()
    from old_cyberdb.scans import scan

    dbname = args.dbname
    scan(dbname)
