def test_table_empty_host(new_cyberdb):
    formatted_data = new_cyberdb.request("host", format="table")

    assert "No data" in formatted_data


def test_table_multiple_hosts(new_cyberdb):
    # Feed multiple hosts
    new_cyberdb.feed("host", ip="1.1.1.1")
    new_cyberdb.feed("host", ip="2.2.2.2", hostname="test")

    # Get queryset and format
    formatted_data = new_cyberdb.request(
        "host", format="table", fields=["ip", "hostname"]
    )
    result = formatted_data
    result_lower = result.lower()

    # Check title
    assert "data" in result_lower

    # Check data presence
    assert "1.1.1.1" in result
    assert "2.2.2.2" in result
    assert "test" in result
