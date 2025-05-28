import json
from datetime import datetime
from io import StringIO
from typing import Any

from cybsuite.cyberdb import BaseFormatter, Metadata


class JSONFormat(BaseFormatter):
    """Format queryset as JSON string."""

    name = "json"
    metadata = Metadata(description="Format to JSON")

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
