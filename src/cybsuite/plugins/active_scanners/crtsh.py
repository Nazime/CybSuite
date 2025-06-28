from datetime import datetime, timezone

from cybsuite.scanners import BasicScanner, Metadata


class CrtshPlugin(BasicScanner):
    name = "crtsh"
    groups = ["root_domain"]
    metadata = Metadata(
        description="Scan for certificates in crt.sh",
        version="0.0.1",
    )
    controls = ["certificate:wildcard"]

    def do_run(self, domain_name: str, exclude_expired: bool = True):
        request_string = f"https://crt.sh?q={domain_name}&output=json"
        if exclude_expired:
            request_string += "&exclude=expired"

        data = self.http.get(request_string).json()

        for row in data:
            common_name = row.get("common_name")
            issuer_name = row.get("issuer_name")
            serial_number = row.get("serial_number")

            # Convert the date fields
            not_before = self._parse_date(row.get("not_before"))
            not_after = self._parse_date(row.get("not_after"))

            if (
                common_name
                and common_name.count(".") == 2
                and common_name.startswith("*.")
            ):
                self.alert("certificate:wildcard", details={"common_name": common_name})

            self.feed(
                "certificate",
                common_name=common_name,
                issuer_name=issuer_name,
                serial_number=serial_number,
                not_before=not_before,
                not_after=not_after,
            )

    @staticmethod
    def _parse_date(date_string: str) -> datetime:
        """
        Converts a string date from crt.sh into a datetime object.
        The date format is assumed to be '%Y-%m-%dT%H:%M:%S'.
        """
        if date_string:
            try:
                d = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
                d = d.replace(tzinfo=timezone.utc)
                return d
            except ValueError:
                # Handle incorrect date formats or fallback
                return None
        return None
