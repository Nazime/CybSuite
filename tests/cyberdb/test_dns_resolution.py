def test_resolve_functions(new_cyberdb):
    # Setup test data for all resolution tests
    new_cyberdb.feed("dns", ip="8.8.8.8", domain_name="dns.google.com")
    new_cyberdb.feed("dns", ip="8.8.4.4", domain_name="dns.google.com")
    new_cyberdb.feed("dns", ip="8.8.8.8", domain_name="google-public-dns-a.google.com")

    # Test resolve_ip function
    assert set(new_cyberdb.resolve_ip("8.8.8.8")) == {
        "dns.google.com",
        "google-public-dns-a.google.com",
    }
    assert set(new_cyberdb.resolve_ip("1.1.1.1")) == set()  # Test non-existent IP

    # Test resolve_domain_name function
    assert set(new_cyberdb.resolve_domain_name("dns.google.com")) == {
        "8.8.8.8",
        "8.8.4.4",
    }
    assert (
        set(new_cyberdb.resolve_domain_name("nonexistent.example.com")) == set()
    )  # Test non-existent domain

    # Test resolve function
    # Test with IP address
    assert set(new_cyberdb.resolve("8.8.8.8")) == {
        "dns.google.com",
        "google-public-dns-a.google.com",
    }

    # Test with domain name
    assert set(new_cyberdb.resolve("dns.google.com")) == {"8.8.8.8", "8.8.4.4"}
