import os
import platform
import pwd
from pathlib import Path

# Update it also in pyproject.toml
VERSION = "0.1.1"
LOGGER_NAME = "cybsuite"


if "CYBSUITE_HOME" in os.environ:
    PATH_CYBSUITE = Path(os.environ["CYBSUITE_HOME"])
else:
    if "CYBSUITE_USER" in os.environ:
        _USER = os.environ["CYBSUITE_USER"]
    elif "SUDO_USER" in os.environ:
        _USER = os.environ["SUDO_USER"]
    elif "USER" in os.environ:
        _USER = os.environ["USER"]
    else:
        _USER = os.getlogin()
    if platform.system() == "Windows":
        _PATH_HOME = Path(os.path.expanduser(f"~{_USER}"))
    else:
        _PATH_HOME = Path(pwd.getpwnam(_USER).pw_dir)
    PATH_CYBSUITE = _PATH_HOME / "cybsuite"


PATH_CYBSUITE = PATH_CYBSUITE.expanduser()
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
