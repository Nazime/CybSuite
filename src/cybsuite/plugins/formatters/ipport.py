from io import StringIO
from typing import Any

from cybsuite.cyberdb import BaseFormatter, Metadata


class IPPortTCPFormatter(BaseFormatter):
    """Format queryset as CSV string."""

    name = "ipport"
    metadata = Metadata(description="Format to ip:port on TCP protocol")

    def format(self, queryset: Any) -> str:
        if not queryset:
            return ""

        output = StringIO()
        for obj in queryset:

            output.write(f"{obj.host.ip}:{obj.port}\n")

        return output.getvalue()
