from io import StringIO
from typing import Any

from cybsuite.cyberdb import BaseFormatter, Metadata


class IPPortTCPFormatter(BaseFormatter):
    """Format queryset as CSV string."""

    name = "ipports_tcp"
    metadata = Metadata(description="Format to ip:port1,port2,port3 on TCP protocol")

    def format(self, queryset: Any) -> str:
        if not queryset:
            return ""

        output = StringIO()
        for host in queryset:
            ports = [str(e.port) for e in host.services.filter(protocol="tcp")]
            if not ports:
                continue
            ports = ",".join(ports)
            output.write(f"{host.ip}:{ports}\n")

        return output.getvalue()
