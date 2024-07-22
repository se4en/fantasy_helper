from typing import Generator, List
import os.path as path

from pytest import fixture
from hydra import compose, initialize
from hydra.utils import instantiate
from hydra.core.global_hydra import GlobalHydra

from fantasy_helper.utils.common import load_config, instantiate_leagues
from fantasy_helper.utils.dataclasses import LeagueInfo


@fixture(scope="session")
def leagues() -> Generator[List[LeagueInfo], None, None]:
    cfg = load_config(config_path="../conf", config_name="config")
    leagues = instantiate_leagues(cfg.leagues)
    yield leagues
