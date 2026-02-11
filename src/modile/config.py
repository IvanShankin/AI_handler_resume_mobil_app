from src.modile.models.config_model import Config

_config: Config = None


def set_config(conf: Config):
    global _config
    _config = conf


def get_config():
    global _config

    if _config is None:
        raise RuntimeError("Config не заполнен")

    return _config