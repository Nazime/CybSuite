from cybsuite.cyberdb import BasePassiveScanner, Metadata


class SmbScanner(BasePassiveScanner):
    name = "smb"
    metadata = Metadata(
        description="Scan for SMB services",
        tags=["default"],
    )
    controls = ["smb:no_signing", "smb:smbv1"]

    def do_run(self):
        for service_smb in self.cyberdb.request("service_smb"):
            service = service_smb.service
            host = service.host
            ip = host.ip
            port = service.port
            # TODO: domain_names will broke uniqueness
            domain_names = "\n".join(self.cyberdb.resolve(ip))
            hostname = host.hostname
            details = {
                "ip": ip,
                "port": port,
                "domain_names": domain_names,
                "hostname": hostname,
            }

            self.control("smb:no_signing", details=details).ko(
                not service_smb.signing, confidence="certain", severity="medium"
            )

            self.control("smb:smbv1", details=details).ko(
                service_smb.smbv1, confidence="certain", severity="medium"
            )
