from datetime import datetime
from io import StringIO
from typing import Any

import yaml
from cybsuite.cyberdb import BaseFormatter, Metadata


class YAMLFormat(BaseFormatter):
    """Format queryset as YAML string."""

    name = "yaml"
    metadata = Metadata(description="Format to YAML")

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
