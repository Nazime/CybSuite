from datetime import datetime
from io import StringIO
from typing import Any

from cybsuite.cyberdb import BaseFormatter, Metadata
from rich.console import Console
from rich.table import Table


class TableFormat(BaseFormatter):
    """Format queryset as a rich table for human reading."""

    name = "table"
    metadata = Metadata(description="Format to a rich table for human reading")

    def _format_value(self, value: Any) -> str:
        """Format a value for human reading.

        Args:
            value: Value to format

        Returns:
            Formatted string
        """
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        if value is None:
            return ""
        return str(value)

    def format(self, queryset: Any) -> str:
        if not queryset:
            return "No data"

        table = Table(title=f"{queryset.model.__name__} Data")

        # Add columns
        for field in queryset.model._meta.fields:
            table.add_column(field.name)

        # Add rows
        for obj in queryset:
            row = [
                self._format_value(getattr(obj, f.name))
                for f in queryset.model._meta.fields
            ]
            table.add_row(*row)

        # Render to string
        console = Console()
        with console.capture() as capture:
            console.print(table)
        return capture.get()
