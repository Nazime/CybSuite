from importlib.metadata import entry_points

from cybsuite.extension import CybSuiteExtension
from koalak.subcommand_parser import SubcommandParser

from .cmd_add import add_cmd_add
from .cmd_get_extract_script import add_cmd_get_extract_script
from .cmd_list import add_cmd_list
from .cmd_review import add_cmd_review

cmd_main = SubcommandParser(
    "cybs-review",
    description="[bold cyan]CybSuite Review CLI[/bold cyan]\n\nYou can manage workspaces with the [green]`cybs-workspace`[/green] command\nYou can interact with data with the [green]`cybs-db`[/green] command",
)

cmd_main.add_group("scanners", description="Scanners")

add_cmd_get_extract_script(cmd_main)
add_cmd_list(cmd_main)  # Main list command for plugins
add_cmd_add(cmd_main)  # Add files command
add_cmd_review(cmd_main)  # Review command

# Add other CLIs from extensions
for extend_function in CybSuiteExtension.load_extend_cli_review_functions():
    extend_function(cmd_main)


def main():
    cmd_main.run()


if __name__ == "__main__":
    main()
