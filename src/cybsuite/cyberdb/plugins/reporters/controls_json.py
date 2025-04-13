import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

from cybsuite.cyberdb import CyberDB
from cybsuite.cyberdb.bases import BaseReporter
from koalak.plugin_manager import Metadata


@dataclass
class ControlOccurrence:
    """Represents a single occurrence of a control check."""

    severity: str
    status: str
    confidence: str
    details: dict


@dataclass
class ObservationOccurrence:
    """Represents a single occurrence of an observation (failed control)."""

    severity: str
    confidence: str
    details: dict


@dataclass
class ControlDefinition:
    """Represents a control definition with its occurrences."""

    name: str
    max_severity: str
    status: str
    total_status_ok: int
    total_status_ko: int
    confidence: str
    total_occurrences: int
    occurrences: list[ControlOccurrence]
    all_keys: list[str] = field(default_factory=list)


@dataclass
class ObservationDefinition:
    """Represents an observation definition (failed control) with its occurrences."""

    name: str
    max_severity: str
    confidence: str
    total_occurrences: int
    occurrences: list[ObservationOccurrence]
    all_keys: list[str] = field(default_factory=list)


@dataclass
class SeverityStats:
    """Statistics for severity levels."""

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0
    unknown: int = 0


@dataclass
class Summary:
    """Overall summary statistics for the report."""

    total_control_definitions: int = 0
    total_control_occurrences: int = 0
    total_observations_definitions: int = 0
    total_observations_occurrences: int = 0
    controls_definitions_by_severity: SeverityStats = field(
        default_factory=SeverityStats
    )
    observations_definitions_by_severity: SeverityStats = field(
        default_factory=SeverityStats
    )
    observations_occurrences_by_severity: SeverityStats = field(
        default_factory=SeverityStats
    )


@dataclass
class ReportData:
    """Complete report data structure."""

    controls: list[ControlDefinition] = field(default_factory=list)
    observations: list[ObservationDefinition] = field(default_factory=list)
    summary: Summary = field(default_factory=Summary)

    def to_dict(self) -> dict:
        """Convert the report data to a dictionary for JSON serialization."""
        return asdict(self)


class ControlsJsonReporter(BaseReporter):
    name = "controls_json"
    metadata = Metadata(
        category="reporters",
        description="Generate JSON report for controls",
    )
    extension = ".json"

    def configure(self, latest_run=None):
        self.latest_run = latest_run
        self.ControlTemplate = self.cyberdb._django_objects["control_definition"]
        self.Controls = self.cyberdb._django_objects["control"]

    def _get_max_severity_and_confidence(
        self, occurrences: list[ControlOccurrence]
    ) -> tuple[str, str]:
        """Get the maximum severity and its corresponding confidence from occurrences."""
        # Get choices from schema
        severity_choices = self.cyberdb.schema["control"]["severity"].choices
        confidence_choices = self.cyberdb.schema["control"]["confidence"].choices

        max_severity = severity_choices[0]  # Lowest severity is first in choices
        max_severity_occurrences = []

        # Find occurrences with max severity
        for occurrence in occurrences:
            current_idx = severity_choices.index(occurrence.severity)
            max_idx = severity_choices.index(max_severity)
            if current_idx > max_idx:
                max_severity = occurrence.severity
                max_severity_occurrences = [occurrence]
            elif current_idx == max_idx:
                max_severity_occurrences.append(occurrence)

        # Get max confidence among occurrences with max severity
        max_confidence = confidence_choices[0]  # Lowest confidence is first in choices
        for occurrence in max_severity_occurrences:
            if confidence_choices.index(
                occurrence.confidence
            ) > confidence_choices.index(max_confidence):
                max_confidence = occurrence.confidence

        return max_severity, max_confidence

    def _update_severity_stats(self, stats: SeverityStats, severity: str) -> None:
        """Update severity statistics."""
        if severity == "critical":
            stats.critical += 1
        elif severity == "high":
            stats.high += 1
        elif severity == "medium":
            stats.medium += 1
        elif severity == "low":
            stats.low += 1
        elif severity == "info":
            stats.info += 1
        elif severity is None:
            stats.unknown += 1

    def do_processing(self):
        # Initialize filter dictionary for control definitions
        control_def_filter_dict = {
            "controls__isnull": False,
        }

        # Add run_object filter if it exists
        if self.latest_run:
            control_def_filter_dict["controls__latest_run"] = self.latest_run

        # Initialize controls filter dictionary
        controls_filter_dict = {}
        if self.latest_run:
            controls_filter_dict["latest_run"] = self.latest_run

        # Fetch control templates with associated controls using the filter dictionary
        control_definitions = self.ControlTemplate.filter(
            **control_def_filter_dict
        ).distinct()

        # Initialize report data
        report_data = ReportData()

        # Process each control template
        for control_definition in control_definitions:
            # Get all occurrences for this control
            occurrences = []
            all_keys = {}  # Use a list to maintain order of first seen

            # Get filtered controls
            controls = control_definition.controls.filter(**controls_filter_dict)
            for control in controls:
                occurrence = ControlOccurrence(
                    severity=control.severity or control_definition.severity,
                    status=control.status,
                    confidence=control.confidence,
                    details=control.details,
                )
                occurrences.append(occurrence)
                # Collect keys in order of first seen
                for key in control.details.keys():
                    if key not in all_keys:
                        all_keys[key] = None

            if not occurrences:
                raise ValueError(
                    f"No occurrences found for control definition: {control_definition.name}, normaly already filtred "
                )

            # Calculate control statistics
            total_occurrences = len(occurrences)
            total_status_ok = sum(1 for occ in occurrences if occ.status == "ok")
            total_status_ko = sum(1 for occ in occurrences if occ.status == "ko")
            max_severity, confidence = self._get_max_severity_and_confidence(
                occurrences
            )

            # Create control definition object
            control_def = ControlDefinition(
                name=control_definition.name,
                max_severity=max_severity,
                status="ko" if total_status_ko > 0 else "ok",
                total_status_ok=total_status_ok,
                total_status_ko=total_status_ko,
                confidence=confidence,
                total_occurrences=total_occurrences,
                occurrences=occurrences,
                all_keys=list(all_keys),  # Use the ordered list
            )

            # Update summary statistics
            report_data.summary.total_control_definitions += 1
            report_data.summary.total_control_occurrences += total_occurrences
            self._update_severity_stats(
                report_data.summary.controls_definitions_by_severity, max_severity
            )

            # Add control to report
            report_data.controls.append(control_def)

            # If there are KO occurrences, create an observation
            if total_status_ko > 0:
                # Create observation occurrences (only from KO controls)
                observation_occurrences = []
                observation_keys = {}  # Use a list to maintain order of first seen
                for occ in occurrences:
                    if occ.status == "ko":
                        observation_occurrences.append(
                            ObservationOccurrence(
                                severity=occ.severity,
                                confidence=occ.confidence,
                                details=occ.details,
                            )
                        )
                        # Collect keys in order of first seen
                        for key in occ.details.keys():
                            if key not in observation_keys:
                                observation_keys[key] = None

                observation = ObservationDefinition(
                    name=control_definition.name,
                    max_severity=max_severity,
                    confidence=confidence,
                    total_occurrences=total_status_ko,
                    occurrences=observation_occurrences,
                    all_keys=list(observation_keys),  # Use the ordered list
                )

                # Update observation statistics
                report_data.summary.total_observations_definitions += 1
                report_data.summary.total_observations_occurrences += total_status_ko
                self._update_severity_stats(
                    report_data.summary.observations_definitions_by_severity,
                    max_severity,
                )
                for occ in observation_occurrences:
                    self._update_severity_stats(
                        report_data.summary.observations_occurrences_by_severity,
                        occ.severity,
                    )

                report_data.observations.append(observation)

        # Save the JSON report
        return report_data.to_dict()

    def run(self, output):
        data = self.do_processing()
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as file:
            json.dump(data, file, indent=2)
