from db.parse.sports import Sports
from db.parse.xbet import XBet
from db.parse.fbref import FbrefParser
from domain.coeffs import CoeffManager
from domain.leagues_info import LeagueInfoManager
from domain.player_stats import PlayerStatsManager
from domain.players import PlayerManager
from domain.users import UserManager
from domain.sources import SourcesManager


xbet = XBet()
sports = Sports()
fbref = FbrefParser()
coeff_manager = CoeffManager(xbet)
user_manager = UserManager()
player_manager = PlayerManager()
player_stats_manager = PlayerStatsManager()
league_info_manager = LeagueInfoManager()
sources_manager = SourcesManager()
