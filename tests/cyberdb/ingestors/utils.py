import os

HERE_PATH = os.path.dirname(__file__)
SCAN_RESULTS_PATH = os.path.join(HERE_PATH, "data")


def get_data_path(*files):
    return os.path.join(SCAN_RESULTS_PATH, *files)
