import csv
from io import StringIO
from typing import Any

from cybsuite.cyberdb import BaseFormatter, Metadata


class CSVFormat(BaseFormatter):
    """Format queryset as CSV string"""

    name = "csv"
    metadata = Metadata(description="Format to CSV")

    def format(self, queryset: Any) -> str:
        if not queryset:
            return ""

        output = StringIO()
        writer = csv.writer(output)

        # Write headers
        writer.writerow([f.name for f in queryset.model._meta.fields])

        # Write data
        for obj in queryset:
            writer.writerow([getattr(obj, f.name) for f in queryset.model._meta.fields])

        return output.getvalue()
