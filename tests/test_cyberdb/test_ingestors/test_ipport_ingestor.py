from cybsuite.cyberdb import CyberDB

from .utils import get_data_path


def test_ipport_ingestor_simple_ip(new_cyberdb: CyberDB):
    path = get_data_path("simple.ip.txt")
    new_cyberdb.ingest("ipport", path)

    assert new_cyberdb.count("host") == 3

    ip_addresses = [e.ip for e in new_cyberdb.request("host")]
    assert ip_addresses == ["10.0.0.1", "10.0.0.2", "10.0.0.3"]


def test_ipport_ingestor_diverse_lines(new_cyberdb: CyberDB, tmp_path):
    data = "10.0.0.1\n10.0.0.2:80\n10.0.0.3:53:udp"
    file_path = tmp_path / "simple.service.txt"
    file_path.write_text(data)

    new_cyberdb.ingest("ipport", file_path)

    assert new_cyberdb.count("host") == 3
    assert new_cyberdb.count("service") == 2

    host_ip_addresses = [e.ip for e in new_cyberdb.request("host")]
    assert host_ip_addresses == ["10.0.0.1", "10.0.0.2", "10.0.0.3"]

    service = new_cyberdb.first("service", port=80)
    assert service.host.ip == "10.0.0.2"
    assert service.port == 80
    assert service.protocol == "tcp"

    service = new_cyberdb.first("service", port=53)
    assert service.host.ip == "10.0.0.3"
    assert service.port == 53
    assert service.protocol == "udp"
