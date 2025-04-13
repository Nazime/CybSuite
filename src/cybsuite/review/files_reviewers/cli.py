from cybsuite.utils import subcommand_add_plugins_filters_arguments
from koalak.subcommand_parser import SubcommandParser

from .runner import run_files_review


def feed_cli(main_cli: SubcommandParser):
    review_types = ["windows"]  # TODO: make it dynamic
    for type_name in review_types:
        review_type_cli = main_cli.add_subcommand(type_name, group="scanners")
        review_type_cli.add_argument("rootpath")
        review_type_cli.add_argument(
            "--force",
            help="Overwrite 'results' folder if exists",
            action="store_true",
        )

        @review_type_cli.register_function
        def run(args):
            run_files_review(
                type_name,
                args.rootpath,
                force=args.force,
                name=args.name,
                category=args.category,
                sub_category=args.sub_category,
                tags=args.tags,
                authors=args.authors,
                controls=args.controls,
            )

        # Add plugins filter arguments
        subcommand_add_plugins_filters_arguments(review_type_cli)
