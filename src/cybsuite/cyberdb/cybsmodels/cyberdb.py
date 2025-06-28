import ipaddress
import os
from io import StringIO
from pathlib import Path
from typing import Iterable, List, Union

from cybsuite.core.logger import get_logger
from cybsuite.cyberdb.db_schema import cyberdb_schema

from ..bases.base_formatter import pm_formatters
from ..bases.base_ingestor import BaseIngestor, pm_ingestors
from ..bases.base_passive_scanner import pm_passive_scanners
from ..consts import PATH_KNOWLEDGEBASE
from .models import BaseCyberDB

logger = get_logger()


class CyberDB(BaseCyberDB):
    _cyberdb = None

    def __init__(self, *args, mission=None, **kwarg):
        super().__init__(*args, **kwarg)
        self.mission = mission

    def clear_knowledgebase(self):
        for entity in cyberdb_schema.filter(tags="knowledgebase"):
            self.clear_one_model(entity.name)

    def clear_no_knowledgebase(self):
        for entity in cyberdb_schema:
            if "knowledgebase" not in entity.tags:
                self.clear_one_model(entity.name)

    def save_knowledgebase(self, folderpath: str):
        self.save_models(folderpath, tags="knowledgebase")

    def save_no_knowledgebase(self, folderpath: str):
        self.save_models(folderpath, tags__ne="knowledgebase")

    def feed_knowledgebase(self, folderpath: str):
        self.feed_models(folderpath, tags="knowledgebase")

    def init_knowledgebase(self):
        self.feed_knowledgebase(PATH_KNOWLEDGEBASE)

    @classmethod
    def from_default_config(cls) -> "CyberDB":
        from cybsuite.cyberdb.config import cyberdb_config

        if cls._cyberdb is None:
            # Prioritize environment variables over default config
            cls._cyberdb = CyberDB(
                os.environ.get("CYBSUITE_DB_NAME", cyberdb_config["name"]),
                user=os.environ.get("CYBSUITE_DB_USER", cyberdb_config["user"]),
                password=os.environ.get(
                    "CYBSUITE_DB_PASSWORD", cyberdb_config["password"]
                ),
                port=int(os.environ.get("CYBSUITE_DB_PORT", cyberdb_config["port"])),
                host=os.environ.get("CYBSUITE_DB_HOST", cyberdb_config["host"]),
            )

        return cls._cyberdb

    # CONVINIENCE METHODS #
    # =================== #

    def resolve_ip(self, ip: str) -> List[str]:
        """Return all domain names that resolve to the given IP"""
        return [e.domain_name for e in self.request("dns", ip=ip)]

    def resolve_domain_name(self, domain_name: str) -> List[str]:
        """Return all IPs that the given domain name resolves to"""
        return [e.ip for e in self.request("dns", domain_name=domain_name)]

    def resolve(self, value: str) -> List[str]:
        """Return all domain names or IPs associated with the given value"""
        try:
            # Try to parse as IP address
            ipaddress.ip_address(value)
            return self.resolve_ip(value)
        except ValueError:
            # If not valid IP, treat as domain name
            return self.resolve_domain_name(value)

    # PLUGINS RELATED METHODS #
    # ======================= #
    # TODO: not finished
    def request(
        self,
        _model_name,
        format: str = None,
        skip: int = None,
        limit: int = None,
        filters: dict = None,
        fields: list = None,
        no_fields: list = None,
        output: str = None,
        **_filters,
    ) -> Iterable[dict]:
        # Ensure no overlapping keys between filters and _filters
        if filters is not None:
            common_keys = set(filters.keys()) & set(_filters.keys())
            if common_keys:
                raise ValueError(f"Duplicate filter keys found: {common_keys}")
            _filters.update(filters)

        data = super().request(_model_name, **_filters)
        if skip is not None:
            data = data[skip:]
        if limit is not None:
            data = data[:limit]

        if format is None:
            return data

        # Get entity schema to determine fields
        entity = self.schema[_model_name]
        # Get field names based on formatter settings
        formatter = pm_formatters[format]()
        fields_objects = [f for f in entity if not f.is_linked_by_related_name]
        if not formatter.include_hidden_fields:
            fields_names = [f.name for f in fields_objects if not f.hidden_in_list]
        else:
            fields_names = [f.name for f in fields_objects]

        # Include or exclude fields
        if fields is not None:
            fields_names = [f for f in fields_names if f in fields]
        if no_fields is not None:
            fields_names = [f for f in fields_names if f not in no_fields]

        # Convert to dict
        data = [
            self.model_to_dict_with_str_fk(row, fields=fields_names) for row in data
        ]

        # Format the data using the specified formatter
        if output is None:
            output = StringIO()
        elif isinstance(output, str):
            # TODO: close file?
            output = open(output, "w")
        formatter.format(data, output, fields_names)

        if isinstance(output, StringIO):
            return output.getvalue()
        else:
            return output

    def scan(self, scanner_name):
        scanner_cls = pm_passive_scanners[scanner_name]
        scanner_instance = scanner_cls(self)
        scanner_instance.run()

    def ingest(
        self, toolname: str, filepaths: Union[str, Path, List[Union[str, Path]]]
    ):
        if isinstance(filepaths, (str, Path)):
            filepaths = [filepaths]

        if toolname == "all":
            return self.ingest_all(filepaths)

        ingestor_cls = pm_ingestors[toolname]
        ingestor_instance = ingestor_cls(self)
        for filepath in filepaths:
            logger.info(f"Ingesting {filepath}")
            try:
                ingestor_instance.run(filepath)
            except Exception as e:
                logger.error(
                    f"Error ingesting file {filepath} with {toolname} ingestor: {type(e).__name__} - {str(e)}"
                )

    def ingest_all(self, root_filepath):
        for e in self.iter_ingest_all(root_filepath):
            pass  ## to iter through all the iterator and ingest every thing

    def iter_ingest_all(self, root_filepath):
        for filepath in utils.iterate_files(root_filepath):
            for (
                ext,
                ingestor_cls,
            ) in BaseIngestor._map_extensions_to_ingestor_cls.items():
                if filepath.endswith(ext):
                    self.ingest(ingestor_cls.name, filepath)
                    yield filepath, ingestor_cls
