import importlib.util
import inspect
from dataclasses import dataclass
from functools import lru_cache
from importlib import import_module
from importlib.metadata import entry_points


def load_from_string(path: str):
    if ":" in path:
        module_path, attr = path.split(":")
        module = import_module(module_path)
        return getattr(module, attr)
    else:
        return import_module(path)


def module_exists(module_path: str) -> bool:
    return importlib.util.find_spec(module_path) is not None


class CybSuiteExtension:
    """Class used to extend CybSuite in other Python libraries
    Library declare"""

    ENTRY_POINT_GROUP_NAME = "cybsuite.extensions"

    def __init__(
        self,
        name: str = None,
        cyberdb_django_app_name: str = None,
        cyberdb_schema: str = None,
        cyberdb_knowledgebase: str = None,
        cyberdb_cli=None,
        extend_cli_review_function: str = None,
    ):

        self.name = name
        self.cyberdb_django_app_name = cyberdb_django_app_name
        self.cyberdb_schema = cyberdb_schema
        self.cyberdb_knowledgebase = cyberdb_knowledgebase
        self.extend_cli_review_function = extend_cli_review_function
        self.cyberdb_cli = cyberdb_cli

    @property
    def cyberdb_django_app_label(self):
        if self.cyberdb_django_app_name is None:
            return None
        return self.cyberdb_django_app_name.split(".")[-1]

    @classmethod
    @lru_cache
    def load_extend_cli_review_functions(cls):
        functions = []
        for extension in cls.load_extensions():
            if extension.extend_cli_review_function is None:
                continue
            func = load_from_string(extension.extend_cli_review_function)
            cls._validate_cli_function(func, "extend_cli_review_function")
            functions.append(func)
        return functions

    @classmethod
    @lru_cache
    def load_extensions(cls) -> list["CybSuiteExtension"]:
        extensions = []
        for cybsuite_extension in entry_points(group=cls.ENTRY_POINT_GROUP_NAME):
            extension_config = cybsuite_extension.load()
            if not isinstance(extension_config, CybSuiteExtension):
                # TODO: improve error (name of distribution + exacte key)
                raise ValueError(
                    f"EntryPoint 'cybsuite.extensions' must return {CybSuiteExtension}'"
                )
            extensions.append(extension_config)
        return extensions

    @classmethod
    def _validate_cli_function(cls, func, name):
        """Checks if func is a function with exactly one positional argument."""
        if func is None:
            return

        if not callable(func):
            raise TypeError(f"{name} must be a function")

        sig = inspect.signature(func)
        params = list(sig.parameters.values())

        if not (
            len(params) == 1
            and params[0].kind
            in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
        ):
            raise TypeError(f"{name} must have exactly one positional argument")

    def __str__(self):
        return f"{self.__class__.__name__}({self.name})"

    def __repr__(self):
        return self.__str__()
