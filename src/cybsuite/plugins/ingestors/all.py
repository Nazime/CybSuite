import os
from functools import cache
from pathlib import Path

from cybsuite.cyberdb import BaseIngestor, Metadata, pm_ingestors


class MasscanIngestor(BaseIngestor):
    name = "all"
    extension = "all"
    metadata = Metadata(description="Ingest all output file")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @cache
    def _get_plugin_instance(self, plugin_name: str):
        plugin_cls = pm_ingestors[plugin_name]
        return plugin_cls(self.cyberdb)

    def do_run(self, filepath):
        path = os.path.abspath(filepath)

        for root, dirs, files in os.walk(path):
            matched = False
            for ingestor_cls in pm_ingestors:
                if ingestor_cls.matches(root):
                    print(f"[MATCH DIR] {root} -> {ingestor_cls.__name__}")
                    ingestor_cls().ingest(root)
                    matched = True
                    break

            if matched:
                # On vide dirs → empêche os.walk de descendre plus loin
                dirs[:] = []
                continue

            # Sinon on teste les fichiers
            for file in files:
                full_path = os.path.join(root, file)
                for ingestor_cls in ingestors:
                    if ingestor_cls.matches(full_path):
                        print(f"[MATCH FILE] {full_path} -> {ingestor_cls.__name__}")
                        ingestor_cls().ingest(full_path)
                        break

        path = Path(filepath)
        if not path.is_dir():
            raise ValueError(f"Expected directory, got {filepath}")
        self.logger.info(f"Ingesting {filepath}")

        # TODO: Implement directory processing

    def match_file(self, ingestor: BaseIngestor, filepath: Path):
        pass
