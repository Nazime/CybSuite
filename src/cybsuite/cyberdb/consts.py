from pathlib import Path

from cybsuite.consts import PATH_CONF_FILE, PATH_CYBSUITE

_here_path = Path(__file__).parent
PATH_DATA = _here_path / "data"
PATH_DB_SCHEMA = PATH_DATA / "schema"
PATH_KNOWLEDGEBASE = PATH_DATA / "knowledgebase"
# PATH_DB_ARCHITECTURE

SSMODELS_MODULE_NAME = "cybsuite.cyberdb.cybsmodels"
SSMODELS_APP_LABEL = "cybsmodels"

# Template paths
PATH_TEMPLATES = PATH_DATA / "templates"
