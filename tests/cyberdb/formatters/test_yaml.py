import yaml


def test_yaml_empty_host(new_cyberdb):
    formatted_data = new_cyberdb.request("host", format="yaml")
    # For empty queryset, should be empty list
    data = yaml.safe_load(formatted_data)
    assert data == []


def test_yaml_multiple_hosts(new_cyberdb):
    # Feed multiple hosts
    new_cyberdb.feed("host", ip="1.1.1.1")
    new_cyberdb.feed("host", ip="2.2.2.2", hostname="test")

    # Get formatted data
    formatted_data = new_cyberdb.request("host", format="yaml")
    data = yaml.safe_load(formatted_data)

    # Check both hosts
    ips = {host["ip"] for host in data}
    assert ips == {"1.1.1.1", "2.2.2.2"}

    # Find the host with hostname
    host_with_name = next(h for h in data if h["ip"] == "2.2.2.2")
    assert host_with_name["hostname"] == "test"
