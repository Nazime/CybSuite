from pathlib import Path


def get_data_path(*paths) -> Path:
    path = Path(__file__).parent / "data"
    for p in paths:
        path = path / p
    return path
