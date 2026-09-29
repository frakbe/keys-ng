from pathlib import Path

from platformdirs import user_config_path, user_data_path

APP_NAME = "keys-ng"
APP_AUTHOR = "Keys NG"


def config_dir() -> Path:
    return Path(user_config_path(APP_NAME, APP_AUTHOR, ensure_exists=True))


def data_dir() -> Path:
    return Path(user_data_path(APP_NAME, APP_AUTHOR, ensure_exists=True))
