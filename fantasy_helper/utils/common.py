from typing import List
from hydra import compose, initialize
from hydra.utils import instantiate
from hydra.core.global_hydra import GlobalHydra
from omegaconf import DictConfig

from fantasy_helper.utils.dataclasses import LeagueInfo


def load_config(
    config_path: str = "../conf", config_name: str = "config"
) -> DictConfig:
    if not GlobalHydra.instance().is_initialized():
        initialize(config_path=config_path, version_base=None)
    cfg = compose(config_name=config_name)

    return cfg


def instantiate_leagues(cfg: DictConfig) -> List[LeagueInfo]:
    all_leagues = instantiate(cfg.leagues)
    active_leagues = list(filter(lambda league: league.is_active, all_leagues))
    return active_leagues
