from cybsuite.cyberdb import BaseIngestor


class MasscanIngestor(BaseIngestor):
    name = "masscan"
    extension = "masscan.txt"
    source = "masscan"  # FIXME:

    def do_run(self, filepath):
        with open(filepath) as f:
            for line in f:
                _, _, _, port_service, _, ip = line.split()
                # Don't need to upsert_host, since upsert_service is doing it
                port, protocol = port_service.split("/")
                port = int(port)
                self.cyberdb.feed("service", host=ip, port=port, protocol=protocol)
