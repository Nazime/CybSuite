from cybsuite.cyberdb import BaseReporter, Metadata
from koalak.utils import data_to_excel


class ExcelReporter(BaseReporter):
    name = "controls_xlsx"
    metadata = Metadata(
        description="Generate Excel report for controls",
    )
    extension = ".xlsx"

    def configure(self, latest_run=None):
        self.latest_run = latest_run

    def run(self, filepath_output, remove_info=True, remove_ok=True):
        from cybsuite.cyberdb import pm_reporters

        json_reporter = pm_reporters["controls_json"](self.cyberdb)
        json_reporter.configure(latest_run=self.latest_run)
        data = json_reporter.do_processing()

        summary = data["summary"]
        controls = data["controls"]

        # Create overview sheet with summary statistics
        overview_data = []

        # Add total counts
        overview_data.append(
            {
                "Type": "Controls",
                "Severity": "All",
                "Definitions": summary["total_control_definitions"],
                "Occurrences": summary["total_control_occurrences"],
            }
        )
        overview_data.append(
            {
                "Type": "Observations",
                "Severity": "All",
                "Definitions": summary["total_observations_definitions"],
                "Occurrences": summary["total_observations_occurrences"],
            }
        )

        # Add severity breakdowns
        for severity in ["critical", "high", "medium", "low", "info", "unknown"]:
            # Controls by severity
            overview_data.append(
                {
                    "Type": "Controls",
                    "Severity": severity.capitalize(),
                    "Definitions": summary["controls_definitions_by_severity"][
                        severity
                    ],
                    "Occurrences": None,
                }
            )
            # Observations by severity
            overview_data.append(
                {
                    "Type": "Observations",
                    "Severity": severity.capitalize(),
                    "Definitions": summary["observations_definitions_by_severity"][
                        severity
                    ],
                    "Occurrences": summary["observations_occurrences_by_severity"][
                        severity
                    ],
                }
            )

        excel = data_to_excel(overview_data, sheet_name="overview")

        # Create summary sheet with control details
        summary_data = []
        for control in controls:
            summary_row = {
                "name": control["name"],
                "max_severity": control["max_severity"],
                "status": control["status"],
                "total_status_ok": control["total_status_ok"],
                "total_status_ko": control["total_status_ko"],
                "confidence": control["confidence"],
                "total_occurrences": control["total_occurrences"],
            }
            summary_data.append(summary_row)

        excel = data_to_excel(summary_data, sheet_name="summary", workbook=excel)

        # Process individual control sheets
        for i, control_definition in enumerate(controls, start=1):
            # Flatten control.details
            controls_details_keys = {}
            for control in control_definition["occurrences"]:
                for key in control["details"]:
                    controls_details_keys[key] = None
            controls_details_keys = list(controls_details_keys)

            data = []
            for control in control_definition["occurrences"]:
                row = {
                    "severity": control["severity"],
                    "status": control["status"],
                    "confidence": control["confidence"],
                }
                for key in controls_details_keys:
                    row[key] = str(control["details"].get(key, ""))
                data.append(row)

            sheet_name = f"{i}_{control_definition['name']}".replace(":", "_").lower()
            excel = data_to_excel(data, sheet_name=sheet_name, workbook=excel)
        excel.save(filepath_output)
