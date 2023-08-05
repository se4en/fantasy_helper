from typing import List
import os.path as path

from pytest import fixture
from hydra import compose, initialize
from hydra.utils import instantiate
from hydra.core.global_hydra import GlobalHydra

from fantasy_helper.utils.dataclasses import LeagueInfo


@fixture(scope="session")
def leagues() -> List[LeagueInfo]:
    # load leagues info
    if not GlobalHydra().is_initialized():
        initialize(config_path="../conf", version_base=None)
    cfg = compose(config_name="config")
    leagues = instantiate(cfg.leagues)
    yield leagues
