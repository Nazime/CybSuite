from cybsuite.cyberdb import CyberDB, pm_ingestors
from cybsuite.cyberdb.cli.utils_cmd import CMD_GROUP_PLUGINS
from koalak.subcommand_parser import SubcommandParser


def add_cli_ingest(cli_main: SubcommandParser):
    subcmd = cli_main.add_subcommand(
        "ingest",
        group=CMD_GROUP_PLUGINS,
        description="Import data from known tools (ex: nmap)",
    )
    help_ingest_cli = """
       Import results of a given tool to the pentestdb database:
       You can recursively import a folder with `pentestdb ingest all <path_folder>`, the selected ingestor is based on the file extension:
       """
    for ingestor in pm_ingestors:
        help_ingest_cli += f"  {ingestor.name.ljust(10)}: {ingestor.extension!r}\n"

    subcmd.add_argument(
        "ingestor_name",
        help="Name of the tool",
        choices=["all"] + list(e.name for e in pm_ingestors),
    )

    subcmd.add_argument("filepath", help="file to import")
    subcmd.register_function(_run)


def _run(args):
    ingestor_name = args.ingestor_name
    filepath = args.filepath
    cyberdb = CyberDB.from_default_config()
    cyberdb.ingest(ingestor_name, filepath)
