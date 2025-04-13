import os
import platform
from pathlib import Path

VERSION = "0.3.6"
LOGGER_NAME = "cybsuite"
if "CYBSUITE_HOME" in os.environ:
    PATH_CYBSUITE = Path(os.environ["CYBSUITE_HOME"])
    PATH_MISSIONS = Path(os.environ["CYBSUITE_MISSIONS"])
    USER = "test"
else:
    if "SUDO_USER" in os.environ:
        USER = os.environ["SUDO_USER"]
    else:
        try:
            USER = os.environ["USER"]
        except KeyError:
            USER = os.getlogin()

    if platform.system() == "Windows":
        _PATH_HOME = Path(os.path.expanduser(f"~{USER}"))
    else:
        import pwd

        _PATH_HOME = Path(pwd.getpwnam(USER).pw_dir)

    # TODO: remove deprecated path missions!
    PATH_MISSIONS = _PATH_HOME / "ssmissions"
    PATH_CYBSUITE = _PATH_HOME / "cybsuite"

CONF_FILE_NAME = "conf.toml"
PATH_CONF_FILE = PATH_CYBSUITE / CONF_FILE_NAME

# Workspace paths
PATH_WORKSPACES = PATH_CYBSUITE / "workspaces"

# Relative paths for workspace structure
FOLDER_NAME_REVIEW = Path("review")
FOLDER_NAME_EXTRACTS = "extracts"
FOLDER_NAME_REPORTS = "reports"
FOLDER_NAME_LOGS = "logs"
FOLDER_NAME_UNARCHIVED = "unarchived"
FILE_NAME_DATA = ".data.json"
