from cybsuite.cyberdb import BaseIngestor

from .utils import validate_ip_address


class IpportIngestor(BaseIngestor):
    name = "ipport"
    extension = "ip.txt"
    extensions = ["ip.txt", "ipport.txt", "ipportprotocol.txt"]
    description = "Handle simple text files containing ip, ip:port, ip:port:protocol"

    def do_run(self, filepath):
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                parts = line.split(":")

                ip = parts[0]
                validate_ip_address(ip)

                if len(parts) == 1:
                    self.cyberdb.feed("host", ip=ip)
                else:
                    port = parts[1] if len(parts) > 1 else None
                    protocol = parts[2] if len(parts) > 2 else "tcp"
                    self.cyberdb.feed("service", host=ip, port=port, protocol=protocol)
