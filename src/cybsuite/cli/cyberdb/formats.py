import csv
import json
from datetime import datetime
from io import StringIO
from typing import Any

import yaml
from koalak.plugin_manager import Plugin, PluginManager, abstract
from rich.console import Console
from rich.table import Table


class BaseFormat(Plugin):
    """Base class for format plugins that convert Django querysets to strings."""

    @abstract
    def format(self, queryset: Any) -> str:
        """Convert queryset to formatted string.

        Args:
            queryset: Django queryset to format

        Returns:
            Formatted string representation
        """
        pass


pm_formats = PluginManager("formats", base_plugin=BaseFormat)


class CSVFormat(BaseFormat):
    """Format queryset as CSV string."""

    name = "csv"

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


class IPFormat(BaseFormat):
    """Format queryset as CSV string."""

    name = "ip"

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


class IPPortFormat(BaseFormat):
    """Format queryset as CSV string."""

    name = "ipport"

    def format(self, queryset: Any) -> str:
        if not queryset:
            return ""

        output = StringIO()
        for obj in queryset:
            output.write(f"{obj.host.ip}:{obj.port}\n")
        return output.getvalue()


class IPPortFormat(BaseFormat):
    """Format queryset as CSV string."""

    name = "ipports_tcp"

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

class IPPortFormat(BaseFormat):
    """Format queryset as CSV string."""

    name = "ipports_udp"

    def format(self, queryset: Any) -> str:
        if not queryset:
            return ""

        output = StringIO()
        for host in queryset:
            ports = [str(e.port) for e in host.services.filter(protocol="udp")]
            if not ports:
                continue
            ports = ",".join(ports)
            output.write(f"{host.ip}:{ports}\n")

        return output.getvalue()

class JSONFormat(BaseFormat):
    """Format queryset as JSON string."""

    name = "json"

    def _serialize_value(self, value: Any) -> Any:
        """Serialize a value to JSON-compatible format.

        Args:
            value: Value to serialize

        Returns:
            JSON-serializable value
        """
        if isinstance(value, datetime):
            return value.isoformat()
        return value

    def format(self, queryset: Any) -> str:
        if not queryset:
            return "[]"

        data = []
        for obj in queryset:
            item = {}
            for field in queryset.model._meta.fields:
                value = getattr(obj, field.name)
                item[field.name] = self._serialize_value(value)
            data.append(item)

        return json.dumps(data, indent=2)


class TableFormat(BaseFormat):
    """Format queryset as a rich table for human reading."""

    name = "table"

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


class YAMLFormat(BaseFormat):
    """Format queryset as YAML string."""

    name = "yaml"

    def _serialize_value(self, value: Any) -> Any:
        """Serialize a value to YAML-compatible format.

        Args:
            value: Value to serialize

        Returns:
            YAML-serializable value
        """
        if isinstance(value, datetime):
            return value.isoformat()
        return value

    def format(self, queryset: Any) -> str:
        if not queryset:
            return "[]"

        data = []
        for obj in queryset:
            item = {}
            for field in queryset.model._meta.fields:
                value = getattr(obj, field.name)
                item[field.name] = self._serialize_value(value)
            data.append(item)

        return yaml.dump(data, sort_keys=False, allow_unicode=True)


if __name__ == "__main__":
    from cybsuite.cyberdb import CyberDB

    db = CyberDB.from_default_config()
    data = db.request("certificate")

    format = pm_formats["yaml"]()
    print(format.format(data))
