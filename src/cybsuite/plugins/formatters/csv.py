import csv
from typing import TextIO

from cybsuite.cyberdb import BaseFormatter, Metadata


class CSVFormat(BaseFormatter):
    """Format queryset as CSV and write directly to output"""

    name = "csv"
    metadata = Metadata(description="Format to CSV")

    def format(self, data: list[dict], output: TextIO, fields: list[str]) -> None:
        writer = csv.writer(output)

        # Write headers
        writer.writerow(fields)

        # Write data rows directly
        for obj in data:  # Use iterator() for memory efficiency
            writer.writerow([obj[f] for f in fields])
