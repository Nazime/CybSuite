import pytest
from cybsuite.review.cli.main_cli import cmd_main
from cybsuite.review.consts import PATH_EXTRACT_SCRIPT_WINDOWS


def test_cli_review_script_windows_command(capsys):
    # Run the command
    cmd_main.run(["script", "windows"])

    # Capture the output
    captured = capsys.readouterr()

    # Read the actual script content
    with open(PATH_EXTRACT_SCRIPT_WINDOWS, "r") as f:
        expected_content = f.read()

    # Compare output with actual script content
    assert captured.out.strip() == expected_content.strip()


def test_cli_review_list_command(capsys):
    # Run the list command
    cmd_main.run(["list"])

    # Capture the output
    captured = capsys.readouterr()
    output = captured.out.lower()

    # Check that bitlocker is present in the output
    expected_keywords = ["bitlocker"]
    for keyword in expected_keywords:
        assert keyword in output, f"Keyword {keyword} not found in list output"

    # Run the list command with windows category filter
    cmd_main.run(["list", "--category", "windows"])

    # Capture the output again
    captured = capsys.readouterr()
    output = captured.out.lower()

    # Check that bitlocker is present in the filtered output
    for keyword in expected_keywords:
        assert keyword in output, f"Keyword {keyword} not found in filtered list output"


def test_cli_review_help_commands(capsys):
    with pytest.raises(SystemExit) as excinfo:
        cmd_main.run(["-h"])
    assert excinfo.value.code == 0

    with pytest.raises(SystemExit) as excinfo:
        cmd_main.run(["list", "-h"])
    assert excinfo.value.code == 0

    with pytest.raises(SystemExit) as excinfo:
        cmd_main.run(["review", "-h"])
    assert excinfo.value.code == 0

    with pytest.raises(SystemExit) as excinfo:
        cmd_main.run(["script", "-h"])
    assert excinfo.value.code == 0
    capsys.readouterr()  # Capture and discard help output
