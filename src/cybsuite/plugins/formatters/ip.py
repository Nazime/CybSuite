from typing import TextIO

from cybsuite.cyberdb import BaseFormatter, Metadata


class IPFormat(BaseFormatter):
    """Format queryset as IP string."""

    name = "ip"
    metadata = Metadata(description="Format to list of IPs")

    def format(self, data: list[dict], output: TextIO, fields: list[str]) -> None:
        seen = set()
        for row in data:
            ip = row.get("ip") or row.get("host")
            if ip and ip not in seen:
                seen.add(ip)
                output.write(ip)
                output.write("\n")
