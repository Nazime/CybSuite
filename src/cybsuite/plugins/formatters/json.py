import json
from typing import TextIO

from cybsuite.cyberdb import BaseFormatter, Metadata


class JSONFormat(BaseFormatter):
    """Format queryset as JSON."""

    name = "json"
    metadata = Metadata(description="Format to JSON array")

    def format(self, data: list[dict], output: TextIO, fields: list[str]) -> None:
        # Write opening bracket
        output.write("[\n")

        first = True
        for item in data:
            if not first:
                output.write(",\n")
            first = False

            # Build and write one object at a time
            json.dump(item, output, indent=2)

        # Write closing bracket
        output.write("\n]")
