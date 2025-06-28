def test_ip_empty(new_cyberdb):
    # Test empty host queryset
    formatted_data = new_cyberdb.request("host", format="ip")
    assert formatted_data == ""

    # Test empty service queryset
    formatted_data = new_cyberdb.request("service", format="ip")
    assert formatted_data == ""


def test_ip_hosts(new_cyberdb):
    # Feed multiple hosts
    new_cyberdb.feed("host", ip="1.1.1.1")
    new_cyberdb.feed("host", ip="2.2.2.2")

    # Get queryset and format
    formatted_data = new_cyberdb.request("host", format="ip")

    # Use sorted list to check order and duplicates
    result = sorted(formatted_data.splitlines())
    assert result == ["1.1.1.1", "2.2.2.2"]


def test_ip_services(new_cyberdb):
    # Feed services with different hosts
    new_cyberdb.feed("service", host="1.1.1.1", port=80, protocol="tcp")
    new_cyberdb.feed("service", host="1.1.1.1", port=443, protocol="tcp")  # Same host
    new_cyberdb.feed("service", host="2.2.2.2", port=22, protocol="tcp")

    # Get queryset and format
    formatted_data = new_cyberdb.request("service", format="ip")

    # Use sorted list to check order and potential duplicates
    result = sorted(formatted_data.splitlines())
    # Should see 1.1.1.1 twice if duplicates are not handled by the formatter
    assert result == ["1.1.1.1", "2.2.2.2"]
