import inspect
from dataclasses import dataclass
from functools import lru_cache
from importlib.metadata import entry_points


class CybSuiteExtension:
    """Class used to extend CybSuite in other Python libraries
    Library declare"""

    def __init__(
        self,
        name: str = None,
        cyberdb_django_app_name: str = None,
        cyberdb_schema: str = None,
        cyberdb_knowledgebase: str = None,
        cyberdb_cli=None,
        extend_cli_review_function=None,
    ):

        self._validate_cli_function(
            extend_cli_review_function, "extend_cli_review_function"
        )
        self._validate_cli_function(cyberdb_cli, "cyberdb_cli")

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
    def load_extensions(cls) -> list["CybSuiteExtension"]:
        extensions = []
        for cybsuite_extension in entry_points(group="cybsuite.extensions"):
            extension_config = cybsuite_extension.load()
            if not isinstance(extension_config, CybSuiteExtension):
                # TODO: improve error (name of distribution + exacte key)
                raise ValueError(
                    f"EntryPoint 'cybsuite.extensions' must return {CybSuiteExtension}'"
                )
            extensions.append(extension_config)
        return extensions

    def _validate_cli_function(self, func, name):
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
