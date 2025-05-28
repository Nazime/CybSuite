import json
from typing import Any

from cybsuite.cyberdb import BaseFormatter, Metadata

from .utils import serialize_value


class JSONFormatter(BaseFormatter):
    """Format queryset as JSON string."""

    name = "json"
    metadata = Metadata(description="Format to JSON")

    def format(self, queryset: Any) -> str:
        if not queryset:
            return "[]"

        data = []
        for obj in queryset:
            item = {}
            for field in queryset.model._meta.fields:
                value = getattr(obj, field.name)
                item[field.name] = serialize_value(value)
            data.append(item)

        return json.dumps(data, indent=2)
