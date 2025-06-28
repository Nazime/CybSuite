from typing import TextIO

from cybsuite.cyberdb import BaseFormatter, Metadata


class IPPortTCPFormatter(BaseFormatter):
    """Format queryset as CSV string."""

    name = "ipports_tcp"
    metadata = Metadata(description="Format to ip:port1,port2,port3 on TCP protocol")

    def format(self, data: list[dict], output: TextIO, fields: list[str]) -> None:
        # First collect all TCP ports per IP
        ip_to_ports = {}
        for row in data:
            ip = row["host"]
            port = row["port"]
            protocol = row["protocol"]

            if protocol == "tcp":
                if ip not in ip_to_ports:
                    ip_to_ports[ip] = set()
                ip_to_ports[ip].add(str(port))

        # Then write out the collected data
        for ip, ports in ip_to_ports.items():
            output.write(f"{ip}:{','.join(sorted(ports))}\n")
