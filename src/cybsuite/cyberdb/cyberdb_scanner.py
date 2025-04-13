from typing import TYPE_CHECKING

from cybsuite.core.logger import get_logger
from cybsuite.core.printer import printer
from cybsuite.utils import log_exception
from django.forms.models import model_to_dict

logger = get_logger()

if TYPE_CHECKING:
    from cybsuite.cyberdb import CyberDB

if TYPE_CHECKING:
    from cybsuite.cyberdb import CyberDB


class Control:
    def __init__(
        self,
        scanner: "CyberDBScanner",
        name,
        *,
        details=None,
        _as_control: bool = True,
    ):
        self.name = name
        self.details = details

        self.scanner = scanner
        self._as_control = _as_control

    def ok(
        self,
        status: bool = None,
        *,
        confidence: str = None,
        severity: str = None,
        justification: str = None,
    ):
        if status is None or status:
            status = "ok"
        else:
            status = "ko"

        self._alert(
            status=status,
            confidence=confidence,
            severity=severity,
            justification=justification,
        )

    def ko(
        self,
        status: bool = None,
        *,
        confidence: str = None,
        severity: str = None,
        justification: str = None,
    ):
        if status is None or status:
            status = "ko"
        else:
            status = "ok"

        self._alert(
            status=status,
            confidence=confidence,
            severity=severity,
            justification=justification,
        )

    def not_applicable(
        self,
        confidence: str = None,
        severity: str = None,
        justification: str = None,
    ):
        # TODO: normally once we call not_applicable (and so on) we can not call other methods like ko
        self._alert(
            status="not_applicable",
            confidence=confidence,
            severity=severity,
            justification=justification,
        )

    def _alert(self, *, status, confidence, severity, justification):
        self.scanner.alert(
            self.name,
            details=self.details,
            status=status,
            confidence=confidence,
            severity=severity,
            justification=justification,
            _as_control=self._as_control,
        )


class CyberDBScanner:
    controls = []

    def __init__(
        self,
        cyberdb: "CyberDB",
        *,
        enable_check_controls_in_db=None,
        enable_printing=None,
        default_scope=None,
        exceptions_path=None,
        enable_print_existing_status=None,
        enabe_printing_feed=None,
    ):
        if enable_printing is None:
            enable_printing = False
        if enabe_printing_feed:
            enabe_printing_feed = True
        if enable_check_controls_in_db:
            enable_check_controls_in_db = True

        self.cyberdb = cyberdb
        self.enforce_controls = False
        self.enforce_confidence = False
        self.enforce_severity = False
        self.enforce_justification = False
        self.enable_check_controls_in_db = enable_check_controls_in_db
        self._nb_identified_obs = 0
        self._nb_new_obs = 0
        self._controls_names = set()
        self.exceptions_path = exceptions_path
        self.aditional_kwargs = {}
        self.aditional_details = {}
        for obs in self.controls:
            if isinstance(obs, dict):
                self._controls_names.add(obs["name"])
            else:
                self._controls_names.add(obs)

        if enable_check_controls_in_db:
            self.fetched_controls = {
                e: cyberdb.first("control_definition", name=e) for e in self.controls
            }
        else:
            self.fetched_controls = {e: e for e in self.controls}

        # Initialize instance logger
        self.logger = get_logger()

        # attributes related to printing/logging #
        # -------------------------------------- #
        self.printer = printer
        # main boolean variable for printing
        self.enable_printing = enable_printing
        self.enabe_printing_feed = enabe_printing_feed
        # if true check for updates (do diff between old/new entry)
        self.enable_update_detection = True
        self.enable_print_existing_status = enable_print_existing_status

        self.track_unprinted_feed_insertions = {}
        self.track_unprinted_controls = {}

    def alert(self, obs_name, *, _as_control=None, **kwargs):
        """Main function to create new control (could also be created with feed)"""
        if _as_control is None:
            _as_control = False

        if obs_name not in self._controls_names:
            raise ValueError(
                f"Control '{obs_name}' must be declared in the plugin '{self.name}'.controls"
            )
        else:
            obs_name = self.fetched_controls[obs_name]

        if self.enforce_controls:
            if "confidence" not in kwargs:
                raise ValueError
            if "severity" not in kwargs:
                raise ValueError
            if "justification" not in kwargs:
                raise ValueError

        if self.enforce_controls:
            if obs_name not in self.controls:
                pass

            pass

        self._nb_identified_obs += 1

        status = kwargs.pop("status", "ko")
        details = kwargs.pop("details", {})
        if details is None:
            details = {}
        if self.aditional_details:
            details.update(self.aditional_details)
        if self.aditional_kwargs:
            kwargs.update(self.aditional_kwargs)

        # use _control instead of control to implement a system forcing
        #  dev to call alert and not feed for controls
        self.feed(
            "_control",
            control_definition=obs_name,
            details=details,
            status=status,
            _as_control=_as_control,
            **kwargs,
        )

    def info(self, *args, **kwargs):
        logger.info(*args, **kwargs)

    def feed(self, model_name, **kwargs):
        """Feed method with exception handling"""
        try:
            return self._feed(model_name, **kwargs)
        except Exception as e:
            log_exception(e, self.exceptions_path)
            # Print the error
            self.logger.error(f"{e} {self.name} {model_name} {kwargs}")
            # self.printer.print(f"{e} {self.name} {model_name} {kwargs}", type="error")

    def _feed(self, model_name, *, _as_control=None, **kwargs):
        if model_name == "control":
            raise ValueError(f"To add new control use alert method instead of feed")
        # use _control instead of control to implement a system forcing
        #  dev to call alert and not feed for controls
        elif model_name == "_control":
            model_name = "control"

        if self.enable_update_detection:
            new_entry, inserted, old_entry = self.cyberdb.feed(
                model_name, True, **kwargs
            )
        else:
            new_entry, inserted = self.cyberdb.feed(model_name, **kwargs)
            old_entry = None

        if self.enable_printing:
            self._print_entry(
                _as_control=_as_control,
                model_name=model_name,
                old_entry=old_entry,
                kwargs=kwargs,
                new_entry=new_entry,
                inserted=inserted,
            )

        return new_entry, inserted

    def ingest(self, name, *args, **kwargs):
        from cybsuite.cyberdb import pm_ingestors

        cls_ingestor = pm_ingestors[name]
        ingestor = cls_ingestor(self.cyberdb)
        ingestor.enable_printing = self.enable_printing
        ingestor.run(*args, **kwargs)

    def control(self, *args, **kwargs) -> Control:
        return Control(self, *args, _as_control=True, **kwargs)

    def check_controls_are_in_db(self):
        db_obs = {e.name for e in self.cyberdb.request("control_definition")}
        not_in_db = []
        for name in self._controls_names:
            if name not in db_obs:
                not_in_db.append(name)

        if not_in_db:
            raise ValueError(f"Following controls are not in DB {not_in_db}")

    # =========================== #
    # Methods related to printing #
    # =========================== #
    def _print_entry(
        self, *, new_entry, old_entry, inserted, kwargs, model_name, _as_control
    ):
        if not self.enabe_printing_feed and model_name != "control":
            return
        feed_status = self.cyberdb.get_feed_status(new_entry, inserted, old_entry)

        if model_name == "control":
            if (
                (feed_status == "existing" and not self.enable_print_existing_status)
                and new_entry.status == "ko"
                and not _as_control
            ):
                obs_name = new_entry.control_definition.name
                if obs_name not in self.track_unprinted_controls:
                    self.track_unprinted_controls[obs_name] = 0
                self.track_unprinted_controls[obs_name] += 1

            # Always print controls
            # Always print updated/new status
            # Always print enable_print_existing status is activated
            if (
                _as_control
                or self.enable_print_existing_status
                or feed_status != "existing"
            ):
                self.print_obs(new_entry)
        else:
            if feed_status == "existing" and not self.enable_print_existing_status:
                # Count it and exit printing function
                if model_name not in self.track_unprinted_feed_insertions:
                    self.track_unprinted_feed_insertions[model_name] = 0
                self.track_unprinted_feed_insertions[model_name] += 1
                return

            if old_entry:
                (
                    kwargs,
                    unpresent_kwargs,
                    updated_kwargs,
                ) = self._diff_between_two_entries(old_entry, new_entry, kwargs)
            else:
                unpresent_kwargs = None
                updated_kwargs = None

            self.printer.print(
                self._dict_to_colored_string(kwargs, unpresent_kwargs, updated_kwargs),
                type="feed",
                plugin_name=self.name,
                feed_status=feed_status,
                model_name=model_name,
            )

    def print_obs(self, obs):
        details_str = ""
        if obs.justification:
            details_str += f"\n  [blue]justification[/blue]: {obs.justification}"
        details_str += self._dict_to_colored_string(obs.details)
        self.printer.print(
            details_str,
            type=obs.status,
            plugin_name=self.name,
            severity=obs.severity,
            confidence=obs.confidence,
            control_name=obs.control_definition.name,
        )

    def _dict_to_colored_string(
        self, details, unpresent_details=None, updated_details: dict = None
    ) -> str:
        """Get rich str to be printed"""
        details = {k: v for k, v in details.items() if v is not None}
        if not details:
            return ""
        # If details is only 1 return first value without key
        elif len(details) == 1:
            first_value = details[list(details)[0]]
            return str(first_value)
        # one per line with colors on keys
        string = "\n" + "\n".join(
            [
                f"  [yellow]{key}[/yellow]: [gray]{value}[/gray]"
                for key, value in details.items()
            ]
        )

        if unpresent_details:
            string += "\n" + "\n".join(
                [
                    f"  [green]{key}[/green]: [gray]{value}[/gray]"
                    for key, value in unpresent_details.items()
                ]
            )
        if updated_details:
            string += "\n" + "\n".join(
                [
                    f"  [blue]{key}[/blue]: [gray]{value}[/gray]"
                    for key, value in updated_details.items()
                ]
            )

        return string

    def _diff_between_two_entries(self, old_entry, new_entry, kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        old_entry = model_to_dict(old_entry)
        old_entry = {
            k: v for k, v in old_entry.items() if v is not None and k in kwargs
        }

        new_entry = model_to_dict(new_entry)
        new_entry = {
            k: v for k, v in new_entry.items() if v is not None and k in kwargs
        }

        unpresent_kwargs = {k: v for k, v in new_entry.items() if k not in old_entry}
        updated_kwargs = {
            k: v
            for k, v in new_entry.items()
            if k in old_entry and new_entry[k] != old_entry.get(k)
        }
        other_kwargs = {k: v for k, v in new_entry.items() if k not in updated_kwargs}
        return other_kwargs, unpresent_kwargs, updated_kwargs
