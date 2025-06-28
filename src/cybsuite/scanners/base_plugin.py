import pathlib
import shlex
import subprocess

import pexpect
import requests
from cybsuite.consts import PATH_CYBSUITE
from cybsuite.cyberdb import CyberDB, CyberDBScanner
from koalak.plugin_manager import Plugin, PluginManager, abstract

pm_home_path = PATH_CYBSUITE / "scanners"


class BasicScanner(CyberDBScanner, Plugin):
    groups = []
    pre_requesties = None

    def __init__(
        self,
        cyberdb: CyberDB,
        allow_print=None,
        enable_check_controls_in_db=None,
    ):
        if allow_print is None:
            allow_print = False
        super().__init__(
            cyberdb,
            exceptions_path=pm_home_path / "exceptions" / f"{self.name}.exceptions.txt",
            enable_check_controls_in_db=enable_check_controls_in_db,
        )
        self.conf = {"timeout": 3}
        self.allow_print = allow_print
        self.http = requests.Session()

    def run(self, *args, **kwargs):
        return self.do_run(*args, **kwargs)

    # ================= #
    # Overwrite methods #
    # ================= #
    @abstract
    def do_run(self, *args, **kwargs):
        pass

    def get_arguments_from_database(self):
        raise NotImplemented

    def was_runned(self):
        raise NotImplemented

    # ============= #
    # Utils methods #
    # ============= #
    def print(self, *args, **kwargs):
        if self.allow_print:
            self.printer.print(*args, type="info", plugin_name=self.name, **kwargs)

    # ============== #
    # Helper methods #
    # ============== #
    def get_output_path(self, *paths):
        paths = "/".join(paths)
        path = PATH_MISSIONS / f"{self.cyberdb.mission}/scanners/{self.name}" / paths
        path = path.expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def execute(
        self, cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=None
    ):
        self.print("execute", shlex.join(cmd_args))
        result = subprocess.run(cmd_args, stdout=stdout, stderr=stderr, timeout=timeout)
        return result

    def popen(self, cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
        self.print("execute", shlex.join(cmd_args))
        result = subprocess.Popen(cmd_args, stdout=stdout, stderr=stderr)
        return result

    def spawn(self, *args, **kwargs):
        timeout = kwargs.pop("timeout", self.conf["timeout"])
        args = [str(arg) for arg in args]
        args = shlex.join(args)
        return pexpect.spawn(args, timeout=timeout, **kwargs)


here = pathlib.Path(__file__).parent
builtin_data_path = here / "data"  # TODO: fix this
pm_scanners = PluginManager(
    "scanners",
    base_plugin=BasicScanner,
    builtin_data_path=builtin_data_path,
    home_path=PATH_CYBSUITE / pm_home_path,
)
