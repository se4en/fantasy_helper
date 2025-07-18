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
    leagues = [
        LeagueInfo(
            name="ClubWorldCup",
            ru_name="КЧМ",
            emoji="🌍",
            squad_id=414835,
            is_active=True,
            xber_url=None,
            betcity_url="https://betcity.ru/ru/line/soccer/602437",
            marathon_url="https://www.marathonbet.com/su/popular/Football/Clubs.+International/Club+World+Cup",
            fbref_league_id=719,
            fbref_table_url=None,
            fbref_schedule_url="https://fbref.com/en/comps/719/schedule/FIFA-Club-World-Cup-Scores-and-Fixtures",
            fbref_playing_time_url="https://fbref.com/en/comps/719/playingtime/FIFA-Club-World-Cup-Stats",
            fbref_shooting_url="https://fbref.com/en/comps/719/shooting/FIFA-Club-World-Cup-Stats",
        ),
        # LeagueInfo(
        #     name="Russia",
        #     ru_name="Россия",
        #     emoji="🇷🇺",
        #     squad_id=316902,
        #     is_active=True,
        #     xber_url="https://1xstavka.ru/line/football/225733-russia-premier-league",
        #     betcity_url="https://betcity.ru/ru/line/soccer/74979",
        #     fbref_league_id=30,
        #     fbref_table_url="https://fbref.com/en/comps/30/Russian-Premier-League-Stats",
        #     fbref_schedule_url="https://fbref.com/en/comps/30/schedule/Russian-Premier-League-Scores-and-Fixtures",
        #     fbref_playing_time_url="https://fbref.com/en/comps/30/playingtime/Russian-Premier-League-Stats",
        #     fbref_shooting_url="https://fbref.com/en/comps/30/shooting/Russian-Premier-League-Stats",
        # ),
        # LeagueInfo(
        #     name="England",
        #     ru_name="Англия",
        #     emoji="🏴󠁧󠁢󠁥󠁮󠁧󠁿",
        #     squad_id=344967,
        #     is_active=True,
        #     xber_url="https://1xstavka.ru/line/football/88637-england-premier-league",
        #     betcity_url="https://betcity.ru/ru/line/soccer/445",
        #     fbref_league_id=9,
        #     fbref_table_url="https://fbref.com/en/comps/9/Premier-League-Stats",
        #     fbref_schedule_url="https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures",
        #     fbref_playing_time_url="https://fbref.com/en/comps/9/playingtime/Premier-League-Stats",
        #     fbref_shooting_url="https://fbref.com/en/comps/9/shooting/Premier-League-Stats",
        #     fbref_passing_url="https://fbref.com/en/comps/9/passing/Premier-League-Stats",
        #     fbref_pass_types_url="https://fbref.com/en/comps/9/passing_types/Premier-League-Stats",
        #     fbref_possesion_url="https://fbref.com/en/comps/9/possession/Premier-League-Stats",
        #     fbref_shot_creation_url="https://fbref.com/en/comps/9/gca/Premier-League-Stats",
        #     sportsmole_name="Premier League",
        # ),
        # LeagueInfo(
        #     name="ChampionsLeague",
        #     ru_name="Лига Чемпионов",
        #     emoji="🇪🇺",
        #     squad_id=379313,
        #     is_active=True,
        #     xber_url="https://1xstavka.ru/en/line/football/118587-uefa-champions-league",
        #     betcity_url="https://betcity.ru/ru/line/soccer/1295",
        #     fbref_league_id=8,
        #     fbref_table_url="https://fbref.com/en/comps/8/Champions-League-Stats",
        #     fbref_schedule_url="https://fbref.com/en/comps/8/schedule/Champions-League-Scores-and-Fixtures",
        #     sportsmole_name="Champions League"
        # )
    ]
    yield leagues
