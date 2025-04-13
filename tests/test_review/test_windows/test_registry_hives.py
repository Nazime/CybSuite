from cybsuite.review.windows.windows_reviewer import WindowsRegistries


def test_registry_hives():
    hive = [
        {
            "properties": {
                "AutoAdminLogon": "0",
                "CachedLogonsCount": "3",
            },
            "path": "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon",
        }
    ]

    hives = WindowsRegistries()
    hives.load_from_list(hive)

    key = hives.get_key(
        "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon"
    )

    assert key["AutoAdminLogon"] == "0"
    assert key["CachedLogonsCount"] == "3"

    # Asserts normalisation is working
    assert (
        hives.get_key(
            "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon"
        )
        == hives.get_key(
            "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon"
        )
        == hives.get_key(
            "hklm\\software\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon"
        )
    )
