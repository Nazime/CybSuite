import xml.etree.ElementTree as ET

from cybsuite.cyberdb import BaseIngestor

# TODO: Licence this file
# TODO: add tag ping in hosts? but dunno how this is written in the XML file
# TODO: map OS name 'os_nmap_name': 'Microsoft Windows 7'
# TODO: implement and test guessed_type

map_nmap_os_gen_to_os_distribution = {
    "7": "7",
    "xp": "xp",
    "2008": "2008",
}

_debug_unmapped_os_gen = set()

TODO = {
    "Microsoft Windows Server 2008 SP1 or Windows Server 2008 R2",
    "Microsoft Windows 7",
    "Microsoft Windows XP SP2",
}

import re

_banner_to_service_regexes = [
    {"regex": r"^SSH", "type": "ssh"},
    {"regex": r"^220 ", "type": "ftp"},
]
for _banner_to_service_regex in _banner_to_service_regexes:
    _banner_to_service_regex["regex"] = re.compile(_banner_to_service_regex["regex"])


def banner_to_service_type(banner: str):
    for regex_rule in _banner_to_service_regexes:
        if regex_rule["regex"].search(banner):
            return regex_rule["type"]


_service_type_map = {
    None: None,
    "tcpwrapped": None,
    "unknown": None,
    "ssl": None,
    # TCP services
    "ftp": "ftp",  # 21
    "ssh": "ssh",  # 22
    "telnet": "telnet",  # 23
    "domain": "dns",  # 53
    "smtp": "smtp",
    "http": "web",  # 80
    "http-proxy": "web",  # 80
    "https": "web",  # 443
    "ldap": "ldap",
    "ldapssl": "ldap",
    "msrpc": "rpc",
    "mysql": "mysql",
    "nfs": "nfs",
    "vnc": "vnc",
    "ms-wbt-server": "rdp",
    "x11": "x11",
    "x11:1": "x11",
    # UDP
    # 161
    "snmp": "snmp",
}

_unmapped_service_type = set()


def normalize_service_type(service_type: str):
    if service_type in _service_type_map:
        return _service_type_map[service_type]
    else:
        _unmapped_service_type.add(service_type)
        return service_type


NMAP_OS_ACCURACY_MIN = 80  # below this percent, we don't check OS


class NmapIngestor(BaseIngestor):
    name = "nmap"
    extension = "nmap.xml"
    # FIXME: source

    def do_run(self, filepath):
        # Parsing the xml file
        try:
            tree = ET.parse(filepath)
        except ET.ParseError:
            # FIXME: raise InvalidFileException
            raise ValueError("File not XML")
        root = tree.getroot()

        # Parse each host separately
        for host_xml in root.iter("host"):
            # parse_host call parse_port which call parse_script
            parsed_result = {
                "hosts": [],
                "services": [],
                "dns": [],
            }
            parsed_services = parsed_result["services"]

            host_dict = {}
            ip = host_xml.find("address").attrib["addr"]
            host_dict["ip"] = ip

            if host_xml.find("status").attrib["reason"] == "user-set":
                # if provided -Pn the host will always be up
                host_is_up_due_to_pn_arg = True
            else:
                host_is_up_due_to_pn_arg = False

            os_xml = host_xml.find("os")
            if os_xml:
                self._parse_xml_os(os_xml, host_dict)

            # TODO: can have many domain names!
            if host_xml.find("hostnames"):
                # This is not the hostname but the domain_name
                domain_name = host_xml.find("hostnames").find("hostname").attrib["name"]
                self.feed("dns", ip=ip, domain_name=domain_name)

            # Parse ports / services
            for xml_port in host_xml.iter("port"):
                self._parse_xml_port(xml_port, parsed_result, host_dict)

            # Check false positive for services #
            # ================================= #
            # If we have a lot of ports! only keep ports with other methods than 'table'
            if len(parsed_services) > 200:
                parsed_services = [
                    e for e in parsed_services if e["nmap_method"] != "table"
                ]

            for service_dict in parsed_services:
                self.feed("service", **service_dict)

            # Check false positive for hosts #
            # ============================== #
            # add a host if we have at least one service (without table method)
            #  or if we didn't specify -sP
            if parsed_services or not host_is_up_due_to_pn_arg:
                self.feed("host", **host_dict)

    def _parse_xml_host(self, xml_host, services):
        host_dict = {}

    def _parse_xml_port(self, xml_port, parsed_result, host_dict):
        # Check if port is open (if filtered or do nothing)
        services = parsed_result["services"]

        state = xml_port.find("state").attrib["state"]
        if state != "open":
            return

        service_dict = {"tags": [], "host": host_dict["ip"]}
        service_tags = service_dict["tags"]

        # Protocol always present in node
        service_dict["protocol"] = xml_port.attrib["protocol"]

        # Portid always present in node
        service_dict["port"] = int(xml_port.attrib["portid"])

        service_xml = xml_port.find("service")
        if service_xml is not None:
            nmap_name = service_xml.attrib.get("name")
            if nmap_name:
                nmap_name = nmap_name.lower()
            service_dict["nmap_name"] = nmap_name
            if nmap_name is not None:
                # If method is "table" => that meens that nmap did a simple mapping
                #  with the default known ports and its database, the service might
                #  be false
                nmap_method = service_xml.attrib["method"]
                service_dict["nmap_method"] = nmap_method
                if nmap_method != "table":
                    service_dict["type"] = normalize_service_type(nmap_name)

                    tunnel = service_xml.attrib.get("tunnel")
                    if tunnel == "ssl":
                        service_tags.append("ssl")

            service_dict["nmap_product"] = service_xml.attrib.get("product")
            if service_dict["nmap_product"] == "Excluded from version scan":
                service_dict["nmap_product"] = None
            service_dict["nmap_version"] = service_xml.attrib.get("version")
            service_dict["version"] = service_dict["nmap_version"]
            service_dict["nmap_extrainfo"] = service_xml.attrib.get("extrainfo")
            service_dict["nmap_devicetype"] = service_xml.attrib.get("devicetype")
            nmap_confidence = service_xml.attrib.get("conf")

            if nmap_confidence:
                nmap_confidence = int(nmap_confidence)
                service_dict["nmap_confidence"] = int(nmap_confidence)

            # FIXME: add xml_cpe?
            """FIXME: implement this
            for cpe_xml in service_xml.iter("cpe"):
                if cpe_xml.text.startswith("cpe:/a"):
                    cpe_service = cpe_xml.text
                else:
                    cpe_os = cpe_xml.text
            """
        services.append(service_dict)
        for xml_script in xml_port.iter("script"):
            self._parse_xml_script(xml_script, parsed_result, service_dict)

        if not service_dict["tags"]:
            del service_dict["tags"]

    def _check_adding_hosts(self, parsed_dict):
        services = parsed_dict["services"]
        if services and len(services) > 200 and all(e["nmap_method"] for e in services):
            return False
        return True

    # TODO: problem when adding! if we have nmap confidence that is 10
    #  and then we parse new file with nmap conf 3 we lose the confidence
    def _parse_xml_os(self, xml_os, host_dict: dict):
        # TODO: add nmap fingerprint
        os_nmap_names = set()

        os_nmap_unique_values = {}
        xml_attributes_names = {
            "osfamily": "family",
            "vendor": "vendor",
            "type": "type",
            "osgen": "generation",
        }
        for attribute_name in xml_attributes_names:
            os_nmap_unique_values[attribute_name] = set()

        for i, xml_osmatch in enumerate(xml_os.iter("osmatch")):
            accuracy = int(xml_osmatch.attrib.get("accuracy"))
            if accuracy < NMAP_OS_ACCURACY_MIN:
                continue

            xml_osclass = xml_osmatch.find("osclass")

            host_dict["os_nmap_name"] = xml_osmatch.attrib.get("name")

            for attribute_name in xml_attributes_names:
                attribute = xml_osclass.attrib.get(attribute_name)
                if attribute:
                    os_nmap_unique_values[attribute_name].add(attribute)

            os_name = xml_osmatch.attrib.get("name")
            if os_name is not None:
                os_nmap_names.add(os_name)

        for nmap_key, pentestdb_key in xml_attributes_names.items():
            value = os_nmap_unique_values[nmap_key]
            if value:
                host_dict[f"os_nmap_{pentestdb_key}"] = list(value)

        if os_nmap_names:
            host_dict["os_nmap_name"] = list(os_nmap_names)

        # fill main OS entries
        if len(os_nmap_unique_values["osfamily"]) == 1:
            host_dict["os_family"] = list(os_nmap_unique_values["osfamily"])[0].lower()

        os_gens = os_nmap_unique_values["osgen"]

        if len(os_gens) == 1:
            os_gen = list(os_gens)[0].lower()
            distribution = map_nmap_os_gen_to_os_distribution.get(os_gen)
            if distribution:
                host_dict["os_distribution"] = distribution

        # Mapp unseen OS gens
        for os_gen in os_gens:
            os_gen = os_gen.lower()
            os_distribution = map_nmap_os_gen_to_os_distribution.get(os_gen)
            if not os_distribution:
                _debug_unmapped_os_gen.add(os_gen)

        # TODO: do the same with OS name

    def _parse_xml_script(self, xml_script, parsed_result: dict, service: dict):
        # TODO: check when there are multiple scripts
        script_id = xml_script.attrib.get("id")
        if script_id == "banner":
            self._check_script_banner(xml_script, service)
        elif script_id == "http-title":
            self._check_script_http_title(xml_script, service)

    def _check_script_banner(self, xml_script, service):
        service["banner"] = xml_script.get("output")

    def _check_script_http_title(self, xml_script, service):
        # TODO: finish me
        for elem in xml_script.iter("elem"):
            if elem.get("key") == "title":
                title = elem.text
                if title:
                    # FIXME: service["http_title"] = title
                    pass


# This variable is not useful, it's here only for debug and adding new services
_seen_nmap_services = [
    "http",
    "msrpc",
    "netbios-ssn",
    "microsoft-ds",
    "ms-wbt-server",
    "amt-soap-https",
    "msmq",
    "mcer-port",
    "domain",
    "kerberos-sec",
    "kpasswd5",
    "http-rpc-epmap",
    "ldapssl",
    "globalcatldap",
    "globalcatldapssl",
    "hosts2-ns",
    "opsmessaging",
    "printer",
    "ipp",
    "jetdirect",
    "dragonidsconsole",
    "su-mit-tg",
    "lmsocialserver",
    "cbt",
    "soap-http",
    "backupexec",
    "wap-wsp",
    "cgms",
    "vrml-multi-use",
    "krb524",
    "radmin",
    "hfcs",
    "mmcc",
    "freeciv",
    "glrpc",
    "cisco-aqos",
    "zeus-admin",
    "bgp",
    "ms-sql-s",
    "radan-http",
    "http-alt",
    "https-alt",
    "smtp",
    "submission",
    "xfer",
    "tacacs",
    "postgresql",
    "pop3",
    "vmrdp",
    "uucp-rlogin",
    "soap",
    "blp3",
    "sun-answerbook",
    "afs3-callback",
    "remoteanything",
    "mit-ml-dev",
    "teradataordbms",
    "nsjtp-data",
    "iscsi",
    "amt-soap-http",
    "upnp",
    "rpcbind",
    "nfs",
    "cslistener",
    "iss-console-mgr",
    "issd",
    "nagios-nsca",
    "snpp",
    "ccproxy-http",
    "zephyr-clt",
    "eklogin",
    "msmq-mgmt",
    "ms-v-worlds",
    "pwgpsi",
    "ibm-mgr",
    "neteh",
    "sip",
    "sane-port",
    "afs3-prserver",
    "blackice-alerts",
    "d-star",
    "rmiregistry",
    "oracle",
    "pichat",
    "scp-config",
    "documentum",
    "vcom-tunnel",
    "fs-agent",
    "filenet-tms",
    "dsf",
    "ms-sql-m",
    "trivnet1",
    "compaqdiag",
    "irc",
    "btx",
    "tsa",
    "jetstream",
    "rtps-dd-mt",
    "interwise",
    "ppp",
    "rwhois",
    "apc-agent",
    "powerchute",
    "powerchuteplus",
    "kyoceranetdev",
    "rtsserv",
    "documentum_s",
]
