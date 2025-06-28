from cybsuite.cyberdb import CyberDB

from .utils import get_data_path


def test_nmap_simple_ping_scan(new_cyberdb: CyberDB):
    path = get_data_path("nmap/ping.nmap.xml")
    new_cyberdb.ingest("nmap", path)

    assert new_cyberdb.count("host") == 1
    assert new_cyberdb.count("service") == 0
    assert new_cyberdb.count("dns") == 1

    hosts = list(new_cyberdb.request("host"))
    host = hosts[0]
    assert host.ip == "8.8.8.8"
    # assert "nmap" in host["source"]

    assert new_cyberdb.count("dns") == 1
    dns_entries = list(new_cyberdb.request("dns"))
    dns_entry = dns_entries[0]
    assert dns_entry.ip == "8.8.8.8"
    assert dns_entry.domain_name == "dns.google"
    # assert dns_entry["source"] == ["nmap"]


def test_nmap_simple_simple_service_scan(new_cyberdb: CyberDB):
    path = get_data_path("nmap/tcp_service_scan.nmap.xml")
    new_cyberdb.ingest("nmap", path)

    assert new_cyberdb.count("host") == 1
    assert new_cyberdb.count("service") == 1
    assert new_cyberdb.count("dns") == 0

    hosts = list(new_cyberdb.request("host"))
    host = hosts[0]
    assert host.ip == "10.10.10.10"
    # assert "nmap" in host["source"]

    service = new_cyberdb.first("service", port=5900)
    assert service.host.ip == "10.10.10.10"
    assert service.protocol == "tcp"
    assert service.port == 5900
    assert service.type == "vnc"
    # assert "nmap" in service["source"]

    assert service.nmap_extrainfo == "protocol 3.8"
    assert service.nmap_name == "vnc"
    assert service.nmap_product == "VNC"
    assert service.nmap_method == "probed"
    assert service.nmap_confidence == 10


def test_nmap_simple_simple_service_scan_ftp(new_cyberdb: CyberDB):
    path = get_data_path("nmap/nmap_service_scan_ftp.nmap.xml")
    new_cyberdb.ingest("nmap", path)

    assert new_cyberdb.count("host") == 1
    assert new_cyberdb.count("service") == 1
    assert new_cyberdb.count("dns") == 0

    hosts = list(new_cyberdb.request("host"))
    host = hosts[0]
    assert host.ip == "10.10.10.10"
    # assert "nmap" in host["source"]

    service = new_cyberdb.first("service", port=21)

    assert service.host.ip == "10.10.10.10"
    assert service.protocol == "tcp"
    assert service.port == 21
    # assert "nmap" in service["source"]
    assert service.type == "ftp"
    assert service.nmap_version == "53.17.9Z"

    assert service.nmap_name == "ftp"
    assert service.nmap_product == "Zebra GK420d or GX430T printer ftpd"
    assert service.nmap_version == "53.17.9Z"
    assert service.nmap_devicetype == "printer"
    assert service.nmap_confidence == 10
    assert service.nmap_method == "probed"
    assert service.nmap_extrainfo is None


def test_nmap_service_scan_https_name_http_with_tunnel_ssl(
    new_cyberdb: CyberDB,
):
    path = get_data_path(
        "nmap/nmap_service_scan_https_name_http_with_tunnel_ssl.nmap.xml"
    )
    new_cyberdb.ingest("nmap", path)

    assert new_cyberdb.count("host") == 1
    assert new_cyberdb.count("service") == 1
    assert new_cyberdb.count("dns") == 0

    hosts = list(new_cyberdb.request("host"))
    host = hosts[0]
    assert host.ip == "10.10.10.10"
    # assert "nmap" in host["source"]

    service = new_cyberdb.first("service", port=443)
    assert service.host.ip == "10.10.10.10"
    assert service.protocol == "tcp"
    assert service.port == 443
    assert service.type == "web"
    assert service.version is None
    # assert "ssl" in service["tags"]

    assert service.nmap_extrainfo is None
    assert service.nmap_name == "http"
    assert service.nmap_product == "Apache httpd"
    assert service.nmap_version is None
    assert service.nmap_devicetype is None
    assert service.nmap_confidence == 10
    # TODO: cpe
    # TODO: mac address


def test_nmap_service_scan_https_name_https_tunnel_ssl(
    new_cyberdb: CyberDB,
):
    path = get_data_path("nmap/nmap_service_scan_https_name_https_tunnel_ssl.nmap.xml")
    new_cyberdb.ingest("nmap", path)

    assert new_cyberdb.count("host") == 1
    assert new_cyberdb.count("service") == 1
    assert new_cyberdb.count("dns") == 0

    hosts = list(new_cyberdb.request("host"))
    host = hosts[0]
    assert host.ip == "10.10.10.10"
    # assert "nmap" in host["source"]

    service = new_cyberdb.first("service", port=443)
    assert service.host.ip == "10.10.10.10"
    assert service.protocol == "tcp"
    assert service.port == 443
    # assert "nmap" in service["source"]
    assert service.type == "web"
    assert service.version is None
    # assert "ssl" in service["tags"]

    assert service.nmap_extrainfo is None
    assert service.nmap_name == "https"
    assert service.nmap_product == "BarracudaHTTP 4.0"
    assert service.nmap_version is None
    assert service.nmap_devicetype is None
    assert service.nmap_confidence == 10
    # TODO: add service fingerprint


def test_nmap_service_scan_https_with_table_method_low_confidence(
    new_cyberdb: CyberDB,
):
    path = get_data_path("nmap/map_service_scan_https_name_https_table_method.nmap.xml")
    new_cyberdb.ingest("nmap", path)

    assert new_cyberdb.count("host") == 1
    assert new_cyberdb.count("service") == 1
    assert new_cyberdb.count("dns") == 0

    hosts = list(new_cyberdb.request("host"))
    host = hosts[0]
    assert host.ip == "10.10.10.10"
    # assert "nmap" in host["source"]

    service = new_cyberdb.first("service", port=443)
    assert service.host.ip == "10.10.10.10"
    assert service.protocol == "tcp"
    assert service.port == 443
    # assert "nmap" in service["source"]
    assert service.type is None
    assert service.version is None
    # assert "ssl" not in service.tags  # Don't add SSL when method is table!

    assert service.nmap_extrainfo is None
    assert service.nmap_name == "https"
    assert service.nmap_product is None
    assert service.nmap_version is None
    assert service.nmap_devicetype is None
    assert service.nmap_confidence == 3


def test_nmap_os_not_found(new_cyberdb: CyberDB):
    path = get_data_path("nmap/os_not_found.nmap.xml")
    new_cyberdb.ingest("nmap", path)

    assert new_cyberdb.count("host") == 1
    assert new_cyberdb.count("service") == 1
    assert new_cyberdb.count("dns") == 0

    hosts = list(new_cyberdb.request("host"))
    host = hosts[0]
    assert host.ip == "10.10.10.10"
    # assert "nmap" in host["source"]

    service = new_cyberdb.first("service", port=8008)
    assert service.host.ip == "10.10.10.10"
    assert service.protocol == "tcp"
    assert service.port == 8008
    assert service.type is None

    assert service.nmap_extrainfo is None
    assert service.nmap_name == "http"
    assert service.nmap_product is None


def test_user_set_host_up(new_cyberdb: CyberDB):
    path = get_data_path("nmap/user_set_host_up.nmap.xml")
    new_cyberdb.ingest("nmap", path)

    assert new_cyberdb.count("host") == 0
    assert new_cyberdb.count("service") == 0
    assert new_cyberdb.count("dns") == 0


def test_false_positive_all_ports_up(new_cyberdb: CyberDB):
    path = get_data_path("nmap/false_positive_all_ports_up.nmap.xml")
    new_cyberdb.ingest("nmap", path)

    assert new_cyberdb.count("host") == 0
    assert new_cyberdb.count("service") == 0
    assert new_cyberdb.count("dns") == 0


def test_nmap_os_multiple_os_all_windows(
    new_cyberdb: CyberDB,
):
    path = get_data_path("nmap/nmap_os_multiple_os_all_windows.nmap.xml")
    new_cyberdb.ingest("nmap", path)

    assert new_cyberdb.count("host") == 1
    assert new_cyberdb.count("service") == 6
    assert new_cyberdb.count("dns") == 1

    entry = new_cyberdb.first("dns")
    assert entry.ip == "10.10.10.10"
    assert entry.domain_name == "pc.test.local"
    # assert "nmap" in entry["source"]

    # Do not care about services in this test #
    host = new_cyberdb.first("host")
    assert host.ip == "10.10.10.10"

    assert host.os_family == "windows"
    # Cannot deduce distribution since we have3 choices
    assert host.os_nmap_family == ["Windows"]
    assert set(host.os_nmap_name) == {
        "Microsoft Windows Server 2008 SP1 or Windows Server 2008 R2",
        "Microsoft Windows XP SP2",
        "Microsoft Windows 7",
    }
    assert set(host.os_nmap_generation) == {"7", "XP", "2008"}
    assert host.os_nmap_vendor == ["Microsoft"]
    assert host.os_nmap_type == ["general purpose"]


def test_nmap_script_banner(
    new_cyberdb: CyberDB,
):
    path = get_data_path("nmap/nmap_script_banner.nmap.xml")
    new_cyberdb.ingest("nmap", path)

    assert new_cyberdb.count("host") == 1
    assert new_cyberdb.count("service") == 1
    assert new_cyberdb.count("dns") == 0

    hosts = list(new_cyberdb.request("host"))
    host = hosts[0]
    assert host.ip == "10.10.10.10"
    # # assert "nmap" in host["source"]

    service = new_cyberdb.first("service", port=22)

    assert service.host.ip == "10.10.10.10"
    assert service.protocol == "tcp"
    assert service.port == 22
    # # assert "nmap" in service["source"]
    assert service.banner == "SSH-2.0-SSH_2.0"
    # assert service["service"] == "ssh"
    assert service.version is None
    # TODO: we should know it's SSH since we have the banner!
    # assert "ssl" not in service.tags  # Don't add SSL when method is table!
