from typing import Any

import yaml
from cybsuite.cyberdb import BaseFormatter, Metadata

from .utils import serialize_value


class YAMLFormat(BaseFormatter):
    """Format queryset as YAML string."""

    name = "yaml"
    metadata = Metadata(description="Format to YAML")

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

        return yaml.dump(data, sort_keys=False, allow_unicode=True)
