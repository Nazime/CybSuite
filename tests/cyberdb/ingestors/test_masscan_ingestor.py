from cybsuite.cyberdb import CyberDB

from .utils import get_data_path


def test_masscan(new_cyberdb: CyberDB):
    path = get_data_path("masscan.txt")
    new_cyberdb.ingest("masscan", path)

    assert new_cyberdb.count("service") == 5
    assert new_cyberdb.count("host") == 2

    host1, host2 = list(new_cyberdb.request("host"))

    assert host1.ip == "10.0.0.1"
    # assert host1["source"] == ["masscan"]  # FIXME

    assert host2.ip == "10.0.0.2"
    # assert host2["source"] == ["masscan"]

    services = list(new_cyberdb.request("service"))
    service = services[0]
    assert service.host == host1
    assert service.port == 443
    assert service.protocol == "tcp"
    # assert "masscan" in service["source"]

    service = services[1]
    assert service.host == host1
    assert service.port == 80
    assert service.protocol == "tcp"
    # assert "masscan" in service["source"]

    service = services[2]
    assert service.host == host1
    assert service.port == 53
    assert service.protocol == "tcp"
    # assert "masscan" in service["source"]

    service = services[3]
    assert service.host == host1
    assert service.port == 53
    assert service.protocol == "udp"
    # assert "masscan" in service["source"]

    service = services[4]
    assert service.host == host2
    assert service.port == 21
    assert service.protocol == "tcp"
    # assert "masscan" in service["source"]
