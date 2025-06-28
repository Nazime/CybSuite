def test_ipports_udp_empty_host(new_cyberdb):
    formatted_data = new_cyberdb.request("host", format="ipports_udp")

    assert formatted_data == ""


def test_ipports_udp_multiple_hosts(new_cyberdb):
    # Feed multiple hosts with UDP services
    new_cyberdb.feed("service", host="1.1.1.1", port=53, protocol="udp")
    new_cyberdb.feed("service", host="1.1.1.1", port=161, protocol="udp")
    new_cyberdb.feed("service", host="2.2.2.2", port=123, protocol="udp")
    # Add a TCP service that should be ignored
    new_cyberdb.feed("service", host="1.1.1.1", port=80, protocol="tcp")

    # Get queryset and format
    formatted_data = new_cyberdb.request("service", format="ipports_udp")

    # Parse lines into dict of ip -> ports
    result = {}
    for line in formatted_data.splitlines():
        ip, ports = line.split(":")
        result[ip] = set(ports.split(","))
    # Check results
    assert result == {"1.1.1.1": {"53", "161"}, "2.2.2.2": {"123"}}
