import json
from typing import Any

from cybsuite.cyberdb import BaseFormatter, Metadata

from .utils import serialize_value


class JSONLFormat(BaseFormatter):
    """Format queryset as JSONL (JSON Lines) string.
    Each record is written as a single line of JSON without pretty printing.
    """

    name = "jsonl"
    metadata = Metadata(description="Format to JSONL (JSON Lines)")

    def format(self, queryset: Any) -> str:
        if not queryset:
            return ""

        output = []
        for obj in queryset:
            item = {}
            for field in queryset.model._meta.fields:
                value = getattr(obj, field.name)
                item[field.name] = serialize_value(value)
            # Dump each object as a single line without indentation
            output.append(json.dumps(item, separators=(",", ":")))

        # Join all lines with newlines
        return "\n".join(output)
