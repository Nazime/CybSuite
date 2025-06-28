from typing import TextIO

import yaml
from cybsuite.cyberdb import BaseFormatter, Metadata


class YAMLFormat(BaseFormatter):
    """Format queryset as YAML."""

    name = "yaml"
    metadata = Metadata(description="Format to YAML")

    def format(self, data: list[dict], output: TextIO, fields: list[str]) -> None:
        yaml.dump(data, output)
