from io import StringIO
from typing import Any

from cybsuite.cyberdb import BaseFormatter, Metadata


class IPFormat(BaseFormatter):
    """Format queryset as IP string."""

    name = "ip"
    metadata = Metadata(description="Format to list of IPs")

    def format(self, queryset: Any) -> str:
        if not queryset:
            return ""

        output = StringIO()
        for obj in queryset:
            try:
                ip = obj.ip
            except:
                ip = obj.host.ip
            output.write(ip)
            output.write("\n")
        return output.getvalue()
