import argparse
import inspect

import koalak
from cybsuite.cyberdb import CyberDB
from cybsuite.scanners import pm_scanners
from cybsuite.scanners.manager import Manager
from koalak.subcommand_parser import SubcommandParser


def print_scanners_table():
    """Print a table of available scanners."""
    rows = []
    for scanner in pm_scanners:
        rows.append(
            {
                "name": scanner.name,
                "groups": ", ".join(getattr(scanner, "groups", [])),
                "description": scanner.metadata.description,
            }
        )
    koalak.containers.print_table(rows)


class ListAndExit(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print_scanners_table()
        parser.exit()


ssrun_cmd = SubcommandParser("cybs-run")
ssrun_cmd.add_argument(
    "--list",
    action=ListAndExit,
    help="List all available scanners and exit",
    nargs=0,
)
ssrun_cmd.add_argument("plugin_name")


@ssrun_cmd.register_function
def run_run(args):
    pass


def main(args=None):
    parsed_args, unparsed_args = ssrun_cmd.parse_known_args(args)
    cyberdb = CyberDB.from_default_config()
    plugin_name = parsed_args.plugin_name

    if plugin_name in pm_scanners:
        plugin_cls = pm_scanners[plugin_name]
    else:
        selected_scanners = [e for e in pm_scanners if plugin_name in e.groups]
        if not selected_scanners:
            raise ValueError(f"scanner or group not existing {plugin_name}")
        plugin_cls = selected_scanners[0]

    scanner = plugin_cls(cyberdb)
    # debug(parsed_args, unparsed_args)

    args, kwargs = parse_function(scanner.do_run, unparsed_args)
    # debug(args, kwargs)
    manager = Manager(cyberdb, print_findings=True)
    manager.run(plugin_name, *args, **kwargs)


def parse_function(func, args_list):
    """
    Parses a function's arguments from a list of command-line-like arguments.

    Parameters:
    func (function): The function whose arguments need to be parsed.
    args_list (list[str]): The list of arguments as if they were provided via command-line.

    Returns:
    tuple: A tuple containing two elements:
        - args (list): Positional arguments for the function.
        - kwargs (dict): Keyword arguments for the function.
    """
    # FIXME: untested GPT code that seems to work
    # Get the function's signature and parameters
    signature = inspect.signature(func)
    parameters = signature.parameters

    # Prepare to collect args and kwargs
    args = []
    kwargs = {}

    # Track the current positional argument index
    positional_index = 0
    is_parsing_kwargs = False

    # Iterate through the provided arguments
    i = 0
    while i < len(args_list):
        arg = args_list[i]

        if arg.startswith("--"):
            # If the argument starts with '--', it's a keyword argument
            key = arg[2:].replace("-", "_")
            if key not in parameters:
                raise ValueError(f"Unexpected keyword argument: {key}")
            is_parsing_kwargs = True

            # The next item in the list should be the value for this keyword argument
            i += 1
            if i >= len(args_list):
                raise ValueError(f"Expected value for argument: {arg}")
            value = args_list[i]

            # Convert value to the correct type based on the function signature
            param = parameters[key]
            kwargs[key] = (
                param.annotation(value) if param.annotation != inspect._empty else value
            )
        elif not is_parsing_kwargs:
            # If we're still parsing positional arguments
            param_list = list(parameters.values())
            if positional_index < len(param_list):
                param = param_list[positional_index]
                if param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD):
                    # Convert value to the correct type based on the function signature
                    value = (
                        param.annotation(arg)
                        if param.annotation != inspect._empty
                        else arg
                    )
                    args.append(value)
                    positional_index += 1
                else:
                    raise ValueError(f"Unexpected positional argument: {arg}")
            else:
                raise ValueError(f"Too many positional arguments provided: {args_list}")
        else:
            raise ValueError(
                f"Unexpected positional argument after keyword argument: {arg}"
            )

        i += 1

    # Handle missing keyword-only arguments that have no default values
    for name, param in parameters.items():
        if param.kind == param.KEYWORD_ONLY and name not in kwargs:
            if param.default == inspect._empty:
                raise ValueError(f"Missing required keyword argument: {name}")
            else:
                kwargs[name] = param.default

    return args, kwargs


# Example usage
def test_parsing():
    # TODO: move this to a test file
    def f(x: int, y: str, *, z: int):
        pass

    assert parse_function(f, ["1", "alpha", "--z", "800"]) == ([1, "alpha"], {"z": 800})

    assert parse_function(f, ["1", "--y", "alpha", "--z", "800"]) == (
        [1],
        {"y": "alpha", "z": 800},
    )

    print("All tests passed.")
