from cybsuite.cyberdb import BasePassiveScanner, Metadata


class CleanPortsScanner(BasePassiveScanner):
    name = "clean_ports"
    metadata = Metadata(
        description="Delete ports 2000 and 5060 which are commonly false positives, and remove hosts that only have these ports"
    )

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
                # TODO: must also check if this host is not added by other source or ping or ...
                #  but for now it's ok
                host.delete()
        # TODO: fixme do not print like this ...

        self.logger.info(
            f"Removed {i_removed_hosts} hosts having only ports 2000 or 5060"
        )
        nb_removed_services = (
            self.cyberdb.request("service").filter(port=2000).delete()[0]
        )
        self.logger.info(f"Removed {nb_removed_services} services with port 2000")
        nb_removed_services = (
            self.cyberdb.request("service").filter(port=5060).delete()[0]
        )
        self.logger.info(f"Removed {nb_removed_services} services with port 5060")
