from cybsuite.cyberdb import BasePassiveScanner, Metadata


class ServicesVersionScanner(BasePassiveScanner):
    name = "services"
    metadata = Metadata(
        description="Search vulnerable services from version and banner.",
        tags=["default"],
    )

    controls = ["service:weak_service", "ldap:anonymous"]

    def do_run(self):
        # Configuration for weak services
        weak_services = {
            514: {
                "service": "rsh",
                "severity": "medium",
                "confidence": "firm",
                "protocol": "tcp",
            },
            21: {
                "service": "ftp",
                "severity": "low",
                "confidence": "firm",
                "protocol": "tcp",
            },
            23: {
                "service": "telnet",
                "severity": "low",
                "confidence": "firm",
                "protocol": "tcp",
            },
        }

        # TODO: later for service also
        # Check for weak services
        for port, config in weak_services.items():
            for service in self.cyberdb.request(
                "service", port=port, protocol=config["protocol"]
            ):
                details = {
                    "service": config["service"],
                    "ip": service.host.ip,
                    "hostname": service.host.hostname,
                    "domain_names": "\n".join(self.cyberdb.resolve(service.host.ip)),
                    "port": service.port,
                    "protocol": service.protocol,
                }
                self.alert(
                    "service:weak_service",
                    details=details,
                    severity=config["severity"],
                    confidence=config["confidence"],
                )

        # Check for LDAP anonymous bind
        for service in self.cyberdb.request(
            "service", nmap_version="(Anonymous bind OK)"
        ):
            details = {
                "ip": service.host.ip,
                "hostname": service.host.hostname,
                "domain_names": "\n".join(self.cyberdb.resolve(service.host.ip)),
                "port": service.port,
                "protocol": service.protocol,
            }
            self.alert(
                "ldap:anonymous",
                details=details,
                severity="medium",
                confidence="certain",
            )
