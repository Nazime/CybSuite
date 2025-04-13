import re
from datetime import datetime, timezone

import dateutil.parser
from cybsuite.review.windows import Metadata, WindowsReviewer


class HotFixReviewer(WindowsReviewer):
    name = "hotfix"
    metadata = Metadata(category="windows", description="Review Get-Hotfix")
    files = {"hotfix": "commands/hotfix.json"}
    controls = ["os:not_updated", "os:updates_are_not_regular"]

    # Private regex pattern for the date format \/Date(1234567890)\/
    _DATE_PATTERN = re.compile(r"\/Date\((\d+)\)\/")

    @classmethod
    def parse_date_value(cls, date_value: str) -> datetime:
        r"""
        Parse a date value string in the format \/Date(1234567890)\/ into a UTC datetime object.

        Args:
            date_value: String in the format \/Date(1234567890)\/

        Returns:
            datetime object with UTC timezone

        Raises:
            ValueError: If the date_value doesn't match the expected format
        """
        match = cls._DATE_PATTERN.match(date_value)
        if not match:
            raise ValueError(
                f"Invalid date format: {date_value}. Expected format: \\/Date(1234567890)\\/"
            )

        timestamp_ms = int(match.group(1))
        # Convert to UTC datetime
        return datetime.fromtimestamp(
            timestamp_ms / 1000, tz=timezone.utc
        )  # Convert milliseconds to seconds

    def do_run(self, files):
        extract_date = self.context.datetime
        filepath = files["hotfix"]
        updates = self.load_json(filepath)
        updates.sort(key=lambda x: self.parse_date_value(x["InstalledOn"]["value"]))

        security_updates = [e for e in updates if e["Description"] == "Security Update"]

        # Check latest security update
        if security_updates:
            latest_security_update = security_updates[-1]
            installed_on = latest_security_update["InstalledOn"]["value"]

            installed_on_date = self.parse_date_value(installed_on)
            delta_days = (extract_date - installed_on_date).days
            if delta_days > 90:
                # TODO: change .alert to .control
                self.alert(
                    "os:not_updated",
                    details={
                        "days": delta_days,
                        # FIXME: makeit as a date and not a str
                        "latest_update": str(installed_on_date),
                    },
                )

        # Check if security updates are regular
        # For example: if we have 1 year between 2 updates it's not good
        for i in range(len(security_updates) - 1, 0, -1):
            j = i - 1
            security_update_i = security_updates[i]
            security_update_j = security_updates[j]
            date_i = self.parse_date_value(security_update_i["InstalledOn"]["value"])
            date_j = self.parse_date_value(security_update_j["InstalledOn"]["value"])

            # Check only for the 2 last years
            if (extract_date - date_i).days > 30 * 12 * 2:
                continue

            delta_days = (date_i - date_j).days
            if delta_days > 90:
                self.alert(
                    "os:updates_are_not_regular",
                    details={
                        # FIXME: makeit as a date and not a str
                        "kb_01": str(security_update_j["HotFixID"]),
                        "kb_02": str(security_update_i["HotFixID"]),
                        "dates": f"{date_j} - {date_i}({delta_days} days)",
                        "days": delta_days,
                    },
                    confidence="certain",
                    justification="Checking the time between two consecutive security update during last 2 years",
                )
