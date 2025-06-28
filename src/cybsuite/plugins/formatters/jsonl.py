import json
from typing import TextIO

from cybsuite.cyberdb import BaseFormatter, Metadata


class JSONLinesFormat(BaseFormatter):
    """Format queryset as JSON Lines (one JSON object per line)."""

    name = "jsonl"
    metadata = Metadata(description="Format to JSON Lines (one JSON object per line)")

    def format(self, data: list[dict], output: TextIO, fields: list[str]) -> None:
        for item in data:
            json.dump(item, output, separators=(",", ":"))
            output.write("\n")
