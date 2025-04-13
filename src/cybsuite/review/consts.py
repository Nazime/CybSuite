from pathlib import Path

_here_path = Path(__file__).parent
PATH_DATA = _here_path / "data"
PATH_EXTRACT_SCRIPTS = PATH_DATA / "extract_scripts"
PATH_EXTRACT_SCRIPT_WINDOWS = PATH_EXTRACT_SCRIPTS / "windows_extract.ps1"


EXTRACT_SCRIPTS = {"windows": PATH_EXTRACT_SCRIPT_WINDOWS}
# Filename inside .zip files that contains all metadata
FILENAME_INFO = "info.json"


REL_PATH_REVIEW_INFO = ".data.json"
