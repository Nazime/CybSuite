from cybsuite.review.files_reviewers.runner import ReviewManager
from cybsuite.utils import subcommand_add_plugins_filters_arguments
from koalak.subcommand_parser import SubcommandParser


def add_cmd_review(main_cli: SubcommandParser):
    review_cli = main_cli.add_subcommand("review", group="scanners")
    review_cli.add_argument(
        "paths",
        nargs="+",
        help="Extracts to review, files or directories",
    )
    review_cli.add_argument(
        "--force",
        help="Overwrite 'results' folder if exists",
        action="store_true",
    )
    review_cli.add_argument(
        "--path",
        help="Path to workspace. If no path is provided, the current workspace will be used",
    )
    review_cli.add_argument(
        "--open-report",
        help="Open the HTML report after generation (default: True)",
        action="store_true",
        dest="open_report",
    )

    # Add plugins filter arguments
    subcommand_add_plugins_filters_arguments(review_cli)
    review_cli.register_function(_run)


def _run(args):
    manager = ReviewManager(
        paths_to_review=args.paths,
        force=args.force,
        name=args.name,
        category=args.category,
        sub_category=args.sub_category,
        tags=args.tags,
        authors=args.authors,
        controls=args.controls,
        open_report=args.open_report,
    )
    manager.run()
