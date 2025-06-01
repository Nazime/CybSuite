import pytest
from cybsuite.cli.workspace.main_cli import cmd_main


def test_cli_workspace_help_commands(capsys):
    with pytest.raises(SystemExit) as excinfo:
        cmd_main.run(["-h"])
    assert excinfo.value.code == 0

    with pytest.raises(SystemExit) as excinfo:
        cmd_main.run(["create", "-h"])
    assert excinfo.value.code == 0

    with pytest.raises(SystemExit) as excinfo:
        cmd_main.run(["switch", "-h"])
    assert excinfo.value.code == 0

    with pytest.raises(SystemExit) as excinfo:
        cmd_main.run(["delete", "-h"])
    assert excinfo.value.code == 0

    with pytest.raises(SystemExit) as excinfo:
        cmd_main.run(["info", "-h"])
    assert excinfo.value.code == 0
    capsys.readouterr()  # Capture and discard help output


def test_cli_workspace_info(capsys):
    # Run the info command
    cmd_main.run(["info"])

    # Capture the output to ensure it runs
    capsys.readouterr()
