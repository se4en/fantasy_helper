from typing import List
from datetime import datetime, timezone
from dataclasses import asdict

from sqlalchemy import func
from sqlalchemy.orm import Session as SQLSession
from hydra import compose, initialize
from hydra.utils import instantiate
from hydra.core.global_hydra import GlobalHydra

from fantasy_helper.db.models.sports_player import SportsPlayer
from fantasy_helper.db.database import Session
from fantasy_helper.parsers.sports import SportsParser
from fantasy_helper.utils.dataclasses import LeagueInfo, SportsPlayerStats
# from fantasy_helper.db.dao.feature_store.fs_lineups import FSLineupsDAO

from fantasy_helper.utils.common import load_config


utc = timezone.utc


class SportsPlayerDAO:
    def __init__(self):
        cfg = load_config(config_path="../../conf")

        self._leagues: List[LeagueInfo] = instantiate(cfg.leagues)
        self._sports_parser = SportsParser(leagues=self._leagues)


    
