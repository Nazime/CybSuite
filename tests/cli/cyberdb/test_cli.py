def test_import_is_not_break():
    from cybsuite.cli.cyberdb import main_cli


def test_cli_list_command(capsys):
    # Import the main CLI
    from cybsuite.cli.cyberdb.main_cli import build_command

    cmd_main = build_command()

    # Run the list command
    cmd_main.run(["list"])

    # Capture the output
    captured = capsys.readouterr()
    output = captured.out.lower()

    # Check that expected columns are present in the output
    expected_keywords = ["nmap", "masscan", "html"]
    for keyword in expected_keywords:
        assert keyword in output, f"Expected keyword {keyword} not found in list output"
