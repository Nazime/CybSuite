import json


def test_json_empty_host(new_cyberdb):
    formatted_data = new_cyberdb.request("host", format="json")
    data = json.loads(formatted_data)
    assert data == []


def test_json_multiple_hosts(new_cyberdb):
    # Feed multiple hosts
    new_cyberdb.feed("host", ip="1.1.1.1")
    new_cyberdb.feed("host", ip="2.2.2.2", hostname="test")

    # Get formatted data
    formatted_data = new_cyberdb.request("host", format="json")
    data = json.loads(formatted_data)

    # Check the data
    assert isinstance(data, list)
    assert len(data) == 2

    # Check both hosts
    ips = {host["ip"] for host in data}
    assert ips == {"1.1.1.1", "2.2.2.2"}

    # Find the host with hostname
    host_with_name = next(h for h in data if h["ip"] == "2.2.2.2")
    assert host_with_name["hostname"] == "test"
