import json


def test_jsonl_empty_host(new_cyberdb):
    formatted_data = new_cyberdb.request("host", format="jsonl")
    # For empty queryset, should be empty string
    assert formatted_data == ""


def test_jsonl_multiple_hosts(new_cyberdb):
    # Feed multiple hosts
    new_cyberdb.feed("host", ip="1.1.1.1")
    new_cyberdb.feed("host", ip="2.2.2.2", hostname="test")

    # Get formatted data
    formatted_data = new_cyberdb.request("host", format="jsonl")

    # Parse each line as JSON
    data = [json.loads(line) for line in formatted_data.splitlines()]

    # Check both hosts
    ips = {host["ip"] for host in data}
    assert ips == {"1.1.1.1", "2.2.2.2"}

    # Find the host with hostname
    host_with_name = next(h for h in data if h["ip"] == "2.2.2.2")
    assert host_with_name["hostname"] == "test"
