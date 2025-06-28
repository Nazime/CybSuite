import functools
from typing import Union

import rich
from cybsuite.cyberdb import CyberDB
from cybsuite.scanners import pm_scanners
from cybsuite_pro.printer import printer

from ..utils import log_exception
from .prerequesites import pm_prerequesites


class Manager:
    def __init__(
        self,
        cyberdb: CyberDB = None,
        print_findings: bool = None,
        enable_check_controls_in_db=None,
    ):
        self.print_findings = print_findings
        self.cyberdb = cyberdb
        self.printer = printer

        # Attributes forwarded to scanners
        self.enable_check_controls_in_db = enable_check_controls_in_db

    def run(self, plugin_name, *args, **kwargs):
        if plugin_name in pm_scanners:
            self._run_one_plugin_one_target(plugin_name, *args, **kwargs)
        else:
            self._run_many_plugins_one_target(plugin_name, *args, **kwargs)

    def _run_one_plugin_one_target(self, plugin_name, *args, **kwargs):
        scanner = self.get_or_instantiate_scanner(plugin_name)
        runned_without_error = True
        try:
            results = scanner.run(*args, **kwargs)
        except Exception as e:
            log_exception(e, scanner.exceptions_path)
            runned_without_error = False
            if self.print_findings:
                self.printer.print(
                    f"{scanner.name} '{e.__class__.__name__}' '{e}'",
                    type="error",
                )

        if scanner.track_unprinted_feed_insertions:
            self.print_info(
                f"Found existing data { scanner.track_unprinted_feed_insertions}"
            )
        if scanner.track_unprinted_controls:
            self.print_info(
                f"Found existing observations {scanner.track_unprinted_controls}"
            )
        if runned_without_error:
            return results

    def _run_many_plugins_one_target(self, group_name: str, *args, **kwargs):
        selected_scanners = [e for e in pm_scanners if group_name in e.groups]
        if not selected_scanners:
            raise ValueError(f"group_name {group_name} not found")

        for plugin_cls in selected_scanners:
            self._run_one_plugin_one_target(plugin_cls.name, *args, **kwargs)

    # TODO: parse function for args/kwargs here
    def control(self, control_name, *args, **kwargs):
        # TODO: not tested not working
        scanners_cls = []
        for scanner_cls in pm_scanners:
            if control_name in scanner_cls.observations:
                scanners_cls.append(scanner_cls)

        if not scanners_cls:
            raise ValueError(f"No scanner scans for control '{control_name}'")

        self.print(
            f"Identified {len(scanners_cls)} scanners for control {control_name}"
        )
        for scanner_cls in scanners_cls:
            self.print(f"Running scanner {control_name.name}")
            self._run_one_plugin_one_target(scanner_cls.name, *args, **kwargs)

    def print(self, *args, **kwargs):
        if self.print_findings:
            rich.print(*args, **kwargs)

    def print_info(self, *args, **kwargs):
        if self.print_findings:
            self.printer.print(*args, type="info", **kwargs)

    # ============= #
    # Utils methods #
    # ============= #
    @functools.cache
    def get_or_instantiate_scanner(self, scanner_name: str):
        scanner_cls = pm_scanners[scanner_name]
        scanner = scanner_cls(
            self.cyberdb,
            enable_check_controls_in_db=self.enable_check_controls_in_db,
        )
        scanner.enable_printing = self.print_findings
        scanner.allow_print = self.print_findings
        if self.enable_check_controls_in_db:
            scanner.check_observations_are_in_db()

        return scanner

    # =================== #
    # AutoPentest methods #
    # =================== #
    def is_prerequisite_ok(self, prerequesite_name):
        prerequesite_cls = pm_prerequesites[prerequesite_name]
        prerequesite = prerequesite_cls(self.cyberdb)
        return prerequesite.run()

    def has_prerequisites(self, attack_name):
        """Check if we have all the prerequesites to run an attack"""
        if attack_name not in pm_scanners:
            raise KeyError(f"Attack '{attack_name}' not registered")

        attack = pm_scanners[attack_name]
        if attack.pre_requesties is None:
            raise ValueError(f"Attack '{attack_name}' does not implement prerequesites")

        for prereq_name in attack.pre_requesties:
            if not self.is_prerequisite_ok(prereq_name):
                return False
        return True

    def get_prerequesite_context(self, prereq):
        return {}

    def auto_run(self, attack: Union[str, "BaseScanner"]):
        if isinstance(attack, str):
            attack = pm_scanners[attack]

        context = {}
        for prereq_name in attack.pre_requesties:
            prereq = pm_prerequesites[prereq_name]
            context.update(self.get_prerequesite_context(prereq))

        for pipeline_action in attack.pipeline:
            pipeline_action = pipeline_action.format(context)
            self.exec_command(pipeline_action)

    def is_attack_already_runned(self, attack_name, target=None):
        if attack_name not in pm_scanners:
            raise KeyError(f"Attack '{attack_name}' not registered")

        attack = attacks[attack_name]
        attack_history_objects = self.cyberdb.django_models["attack_history"].objects

        if attack.type == attack.TYPE_ONCE:
            return attack_history_objects.filter(
                name=attack_name, status="finished"
            ).exists()

    def auto_fake_run(self, attack_name, arguments=None, status=None):
        if attack_name not in attacks:
            raise KeyError(f"Attack '{attack_name}' not registered")

        attack = attacks[attack_name]

        if status is None:
            status = "runned"

        if arguments is None:
            arguments = {}

        attack_history_objects = self.cyberdb.django_models["attack_history"].objects
        attack_history_objects.create(
            name=attack_name, status=status, arguments=arguments
        )
