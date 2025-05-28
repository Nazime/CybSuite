from cybsuite.cyberdb import BaseIngestor, Metadata


class MasscanIngestor(BaseIngestor):
    name = "masscan"
    extension = "masscan.txt"
    metadata = Metadata(description="Ingest masscan output file")

    def do_run(self, filepath):
        with open(filepath) as f:
            for line in f:
                _, _, _, port_service, _, ip = line.split()
                port, protocol = port_service.split("/")
                port = int(port)
                if protocol == "icmp":
                    # ping
                    # TODO: unitest ICMP
                    self.cyberdb.feed("host", ip=ip)
                else:
                    self.cyberdb.feed("service", host=ip, port=port, protocol=protocol)
