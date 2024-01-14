from hydra import compose, initialize
from hydra.core.global_hydra import GlobalHydra
from omegaconf import DictConfig


def load_config(
    config_path: str = "../conf", config_name: str = "config"
) -> DictConfig:
    if not GlobalHydra().is_initialized():
        initialize(config_path=config_path, version_base=None)
    cfg = compose(config_name=config_name)

    return cfg
