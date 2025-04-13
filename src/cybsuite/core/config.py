from koalak.config import Config

from ..consts import PATH_CONF_FILE

_default_config = {
    "workspaces": {"current": "default"},
    "cyberdb": {
        "name": "cyberdb_default",
        "user": "postgres",
        "password": "postgres",
        "host": "127.0.0.1",
        "port": 5432,
    },
}

root_config = Config(PATH_CONF_FILE, default_data=_default_config)
workspaces_config: Config = root_config["workspaces"]
