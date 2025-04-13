from cybsuite.review.consts import EXTRACT_SCRIPTS
from koalak.subcommand_parser import SubcommandParser


def add_cmd_get_extract_script(cmd_main: SubcommandParser):
    subcmd = cmd_main.add_subcommand(
        "script",
        description="Get platform-specific extraction scripts for configuration gathering",
    )

    subcmd.add_argument(
        "type",
        choices=list(EXTRACT_SCRIPTS.keys()),
        help="Type of extraction script to retrieve (e.g., windows, linux)",
    )
    subcmd.register_function(_run)


def _run(args):
    script_path = EXTRACT_SCRIPTS[args.type]
    with open(script_path) as f:
        data = f.read()
    print(data)
