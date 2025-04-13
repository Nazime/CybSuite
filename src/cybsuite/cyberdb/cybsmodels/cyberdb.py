from pathlib import Path
from typing import List, Union

from cybsuite.cyberdb.db_schema import cyberdb_schema

from ..bases.base_ingestor import BaseIngestor, pm_ingestors
from ..consts import PATH_KNOWLEDGEBASE
from .models import BaseCyberDB


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
            cls._cyberdb = CyberDB(
                cyberdb_config["name"],
                user=cyberdb_config["user"],
                password=cyberdb_config["password"],
                port=cyberdb_config["port"],
                host=cyberdb_config["host"],
            )

        return cls._cyberdb

    def resolve_ip(self, ip: str) -> List[str]:
        """Return all domain names to that specific IP"""
        return [e["domain_name"] for e in self.request("dns", ip=ip)]

    def ingest(self, toolname: str, filepath: Union[str, Path]):
        if toolname == "all":
            return self.ingest_all(filepath)

        ingestor_cls = pm_ingestors[toolname]
        ingestor_instance = ingestor_cls(self)
        ingestor_instance.run(filepath)

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
