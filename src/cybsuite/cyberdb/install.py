from pathlib import Path

from .consts import PATH_CYBSUITE


def init_folder():
    """Init home structure"""
    if not Path.is_dir(PATH_CYBSUITE):
        Path.mkdir(PATH_CYBSUITE, parents=True)


def install():
    init_folder()

    # This line will create the config file
    from .config import cyberdb_config
