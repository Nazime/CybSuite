from typing import TextIO

from cybsuite.cyberdb import BaseFormatter, Metadata


class IPPortTCPFormatter(BaseFormatter):
    """Format queryset as CSV string."""

    name = "ipport"
    metadata = Metadata(description="Format to ip:port on TCP protocol")

    def format(self, data: list[dict], output: TextIO, fields: list[str]) -> None:
        for row in data:
            host = row.get("host", {})
            if host and "ip" in host and "port" in row:
                output.write(f"{host['ip']}:{row['port']}\n")
