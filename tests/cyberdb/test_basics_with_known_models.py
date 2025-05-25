def test_simple_model_host(new_cyberdb):
    assert new_cyberdb.count("host") == 0

    new_cyberdb.feed("host", ip="1.1.1.1")
    assert new_cyberdb.count("host") == 1
    entry = new_cyberdb.first("host")
    assert entry.ip == "1.1.1.1"

    # same thing do nothing
    new_cyberdb.feed("host", ip="1.1.1.1")
    assert new_cyberdb.count("host") == 1
    entry = new_cyberdb.first("host")
    assert entry.ip == "1.1.1.1"


def test_service_one_to_many_relation(new_cyberdb):
    assert new_cyberdb.count("host") == 0
    assert new_cyberdb.count("service") == 0

    new_cyberdb.feed("service", host="1.1.1.1", port=80, protocol="tcp")

    assert new_cyberdb.count("host") == 1
    assert new_cyberdb.count("service") == 1
    entry = new_cyberdb.first("host")
    assert entry.ip == "1.1.1.1"

    entry = new_cyberdb.first("service")
    assert entry.port == 80
    assert entry.protocol == "tcp"
    assert entry.host.ip == "1.1.1.1"

    # Same thing do nothing
    new_cyberdb.feed("service", host="1.1.1.1", port=80, protocol="tcp")

    assert new_cyberdb.count("host") == 1
    assert new_cyberdb.count("service") == 1
    entry = new_cyberdb.first("host")
    assert entry.ip == "1.1.1.1"

    entry = new_cyberdb.first("service")
    assert entry.port == 80
    assert entry.protocol == "tcp"
    assert entry.host.ip == "1.1.1.1"
