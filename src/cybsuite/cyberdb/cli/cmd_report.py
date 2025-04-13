from cybsuite.cyberdb import CyberDB, pm_ingestors, pm_reporter
from cybsuite.cyberdb.cli.utils_cmd import CMD_GROUP_PLUGINS
from koalak.subcommand_parser import SubcommandParser


def add_cli_report(cli_main: SubcommandParser):
    subcmd = cli_main.add_subcommand(
        "report", group=CMD_GROUP_PLUGINS, description="Generate report"
    )
    subcmd.add_argument("type", choices=[e.name for e in pm_reporter])
    subcmd.add_argument("output")
    subcmd.register_function(_run)


def _run(args):
    type = args.type
    output = args.output

    cls_reporter = pm_reporter[type]
    db = CyberDB.from_default_config()
    reporter = cls_reporter(db)
    reporter.run(output)
