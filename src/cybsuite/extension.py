import inspect
from dataclasses import dataclass
from functools import lru_cache
from importlib.metadata import entry_points


# TODO: move this to cybsuite top module
class CybSuiteExtension:
    """Class used to extend CybSuite in other Python libraries
    Library declare"""

    def __init__(
        self,
        cyberdb_django_app_name: str = None,
        cyberdb_schema: str = None,
        cyberdb_knowledgebase: str = None,
        cbx_review_cli=None,
        cyberdb_cli=None,
    ):

        self._validate_cli_function(cbx_review_cli, "cbx_review_cli")
        self._validate_cli_function(cyberdb_cli, "cyberdb_cli")

        self.cyberdb_django_app_name = cyberdb_django_app_name
        self.cyberdb_schema = cyberdb_schema
        self.cyberdb_knowledgebase = cyberdb_knowledgebase
        self.cbx_review_cli = cbx_review_cli
        self.cyberdb_cli = cyberdb_cli

    @property
    def cyberdb_django_app_label(self):
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
