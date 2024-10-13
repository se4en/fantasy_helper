from typing import Dict, Any, List, Literal, Optional, Tuple
import os
import logging
import json
import pytz

import requests
import iso8601

from fantasy_helper.utils.dataclasses import LeagueInfo, SportsPlayerStats, SportsTourInfo


class SportsParser:
    def __init__(
        self,
        leagues: List[LeagueInfo],
        url: str = "https://www.sports.ru/gql/graphql/",
        queries_path: Optional[str] = None,
    ):
        self._url = url
        if queries_path is not None:
            self._queries_path = queries_path
        else:
            self._queries_path = os.path.join(os.path.dirname(__file__), "/queries")

        self._leagues = {l.name: l.squad_id for l in leagues if l.squad_id is not None and l.is_active}

    def _get_query_body(
        self, query_name: Literal["squad", "tournament"]
    ) -> Optional[str]:
        fname = os.path.join(self._queries_path, f"{query_name}.graphql")

        if os.path.exists(fname):
            with open(fname, "r") as f:
                return f.read()
        else:
            # TODO log incorrect query file name
            return None

    def _request_for_specific_id(
        self, 
        id: int, 
        query_name: Literal["squad", "tournament", "season", "players"],
        id_type: Literal["$squadID", "$seasonID"] = "$squadID"
    ) -> Optional[dict]:
        headers = {"Content-Type": "application/json"}
        body = self._get_query_body(query_name)
        if body is None:
            return None
        body = body.replace(id_type, str(id))

        response = requests.request(
            "POST",
            self._url,
            headers=headers,
            data=json.dumps({"query": body, "variables": {}}),
        )

        if response.status_code == 200:
            return json.loads(response.text)
        else:
            # TODO log bad response for graphql
            return None

    def _get_season_id(
        self, squad_id: int
    ) -> Optional[int]:
        data = self._request_for_specific_id(squad_id, "season")
        if data is None:
            return None

        query_id = list(data["data"].keys())[0]  
        return data["data"][query_id]["squads"][0]["season"]["id"]

    def _parse_tour_info(self, league_name: str, tour_info: Optional[Dict]) -> Optional[SportsTourInfo]:
        if tour_info is None:
            return None
        return SportsTourInfo(
            league_name=league_name,
            number=int(tour_info["name"].split(" ")[0]),
            matches_count=len(tour_info["matches"]),
            deadline=iso8601.parse_date(tour_info["startedAt"]).replace(
                tzinfo=pytz.UTC
            ),
            status=tour_info["status"],
        )

    def get_schedule(self, league_name: str) -> Optional[List[SportsTourInfo]]:
        if league_name not in self._leagues:
            return None

        squad_id = self._leagues[league_name]
        data = self._request_for_specific_id(squad_id, "tournament")
        if data is None:
            return None

        result = []
        query_id = list(data["data"].keys())[0]
        for tour_info in data["data"][query_id]["squads"][0]["season"]["tours"]:
            result.append(self._parse_tour_info(league_name, tour_info))

        return result

    def get_current_tour(self, league_name: str) -> Optional[SportsTourInfo]:
        schedule = self.get_schedule(league_name)
        if schedule is None:
            return None

        for tour in schedule:
            if tour.status == "OPENED":
                return tour
            
        return None

    def get_next_tour(self, league_name: str) -> Optional[SportsTourInfo]:
        schedule = self.get_schedule(league_name)
        if schedule is None:
            return None

        for tour in schedule:
            if tour.status == "NOT_STARTED":
                return tour

        return None

    def get_players_stats_info(self, league_name: str) -> Optional[List[SportsPlayerStats]]:
        if league_name not in self._leagues:
            logging.info(f"Wrong league_name={league_name} in get_deadline")
            return None

        season_id = self._get_season_id(self._leagues[league_name])
        players_data = self._request_for_specific_id(season_id, "players", id_type="$seasonID")
        current_tour = self.get_current_tour(league_name)
        tour_number = current_tour.number if current_tour is not None else None

        result = []
        if "data" not in players_data:
            return None
        query_id = list(players_data["data"].keys())[0]
        for player_data in players_data["data"][query_id]["season"]["players"]["list"]:
            player_data = player_data.get("player", None)
            if player_data is None:
                pass

            sports_id = player_data.get("id", None)
            name = player_data.get("name", None)
            if not isinstance(sports_id, int) or not isinstance(name, str):
                pass

            status = player_data.get("status", None) or {}
            team = player_data.get("team", None) or {}
            seasonScoreInfo = player_data.get("seasonScoreInfo", None) or {}
            gameStat = player_data.get("gameStat", None) or {}

            result.append(
                SportsPlayerStats(
                    sports_id=sports_id,
                    name=name,
                    league_name=league_name,
                    tour=tour_number,
                    role=player_data.get("role", None),
                    price=player_data.get("price", None),
                    percent_ownership=status.get("percentOwnership", None),
                    team_name=team.get("name", None),
                    place=seasonScoreInfo.get("place", None),
                    score=seasonScoreInfo.get("score", None),
                    average_score=seasonScoreInfo.get("averageScore", None),
                    goals=gameStat.get("goals", None),
                    assists=gameStat.get("assists", None),
                    goals_conceded=gameStat.get("goalsConceded", None),
                    yellow_cards=gameStat.get("yellowCards", None),
                    red_cards=gameStat.get("redCards", None),
                    field_minutes=gameStat.get("fieldMinutes", None),
                    saves=gameStat.get("saves", None)
                )
            )

        return result

    def get_tour_transfers(self, squad_id: int) -> Optional[bool]:
        data = self._request_for_specific_id(squad_id, "squad")
        if data is None:
            return None

        query_id = data["data"].keys()[0]
        tour = data["data"][query_id]["squads"][0]["currentTourInfo"]["tour"]
        all_transfers = tour["constraints"]["totalTransfers"]
        transfers_left = tour["transfersLeft"]

        return all_transfers != transfers_left
