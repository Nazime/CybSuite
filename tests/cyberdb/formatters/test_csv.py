import csv
from io import StringIO


def test_csv_empty_host(new_cyberdb):
    result = new_cyberdb.request("host", format="csv")
    # For empty queryset, should be empty string
    assert result != ""
    assert "ip" in result
    assert "," in result


def test_csv_multiple_hosts(new_cyberdb):
    # Feed multiple hosts
    new_cyberdb.feed("host", ip="1.1.1.1")
    new_cyberdb.feed("host", ip="2.2.2.2", hostname="test")

    # Get formatted data
    result = new_cyberdb.request("host", format="csv")

    # Parse CSV using StringIO
    output = StringIO(result)
    reader = csv.DictReader(output)
    data = list(reader)

    # Check both hosts
    ips = {host["ip"] for host in data}
    assert ips == {"1.1.1.1", "2.2.2.2"}

    # Find the host with hostname
    host_with_name = next(h for h in data if h["ip"] == "2.2.2.2")
    assert host_with_name["hostname"] == "test"
