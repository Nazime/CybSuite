from typing import TextIO

from cybsuite.cyberdb import BaseFormatter, Metadata
from rich.console import Console
from rich.table import Table


class TableFormat(BaseFormatter):
    """Format queryset as a rich table for human reading."""

    name = "table"
    metadata = Metadata(description="Format to a rich table for human reading")

    include_hidden_fields = False

    def format(self, data: list[dict], output: TextIO, fields: list[str]) -> None:
        if not data:
            output.write("No data")
            return

        table = Table(title="Data")

        # Add columns and rows
        for field in fields:
            table.add_column(field)

        for row in data:
            table.add_row(*[str(row[f]) if row[f] is not None else "" for f in fields])

        Console(file=output).print(table)
