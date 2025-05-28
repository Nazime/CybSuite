from cybsuite.cyberdb import BasePassiveScanner


class IpportIngestor(BasePassiveScanner):
    name = "clean_ports"

    def do_run(self):
        i_removed_hosts = 0

        for host in self.cyberdb.request("host"):
            services = host.services.all()
            service_ports = {service.port for service in services}

            # Check if only suspicious ports are present
            false_positive_ports = {2000, 5060}
            if service_ports.issubset(false_positive_ports):
                i_removed_hosts += 1
                # print(f'Deleting host {host.ip} - only has suspicious ports {service_ports}')
                host.delete()
        # TODO: fixme
        if i_removed_hosts:
            print(f"Removed {i_removed_hosts} hosts")

        print(self.cyberdb.request("service").filter(port=2000).delete())
        print(self.cyberdb.request("service").filter(port=5060).delete())


class TagDC(BasePassiveScanner):
    name = "tag_dc"
    descriptions = "All hosts that have port 389 445 and 88 will have 'dc' tag"

    def do_run(self):
        for host in self.db.request("host", services__port=88).filter(
            services__port=389
        ):
            pass
            # add tag
