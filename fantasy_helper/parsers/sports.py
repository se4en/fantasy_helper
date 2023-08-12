from typing import Dict, Any, List, Literal, Optional, Tuple
import os
import logging
import json
import pytz

import requests
import iso8601

from fantasy_helper.utils.dataclasses import LeagueInfo


class SportsParser:
    def __init__(
        self,
        leagues: List[LeagueInfo],
        url: str = "https://www.sports.ru/gql/graphql/",
        queries_path: Optional[str] = None,
    ):
        self.__url = url
        if queries_path is not None:
            self.__queries_path = queries_path
        else:
            self.__queries_path = os.path.join(os.path.dirname(__file__), "/queries")

        self.__leagues = {l.name: l.squad_id for l in leagues if l.squad_id is not None}

    def __get_query_body(
        self, query_name: Literal["squad", "tournament"]
    ) -> Optional[str]:
        fname = os.path.join(self.__queries_path, f"{query_name}.graphql")

        if os.path.exists(fname):
            with open(fname, "r") as f:
                return f.read()
        else:
            # TODO log incorrect query file name
            return None

    def __request_for_squad_id(
        self, squad_id: int, query_name: Literal["squad", "tournament"]
    ) -> Optional[dict]:
        headers = {"Content-Type": "application/json"}
        body = self.__get_query_body(query_name)
        if body is None:
            return None
        body = body.replace("$squadID", str(squad_id))

        response = requests.request(
            "POST",
            self.__url,
            headers=headers,
            data=json.dumps({"query": body, "variables": {}}),
        )

        if response.status_code == 200:
            return json.loads(response.text)
        else:
            # TODO log bad response for graphql
            return None

    def __get_current_tour(
        self, squad_id: int
    ) -> Tuple[Optional[dict], Optional[dict]]:
        cur_tour, next_tour = None, None
        data = self.__request_for_squad_id(squad_id, "tournament")
        if data is None:
            return cur_tour, next_tour

        # looking for current tour
        query_id = list(data["data"].keys())[0]
        for tour in data["data"][query_id]["squads"][0]["season"]["tours"]:
            if cur_tour is not None:
                next_tour = tour
                break
            elif tour["status"] == "OPENED":
                cur_tour = tour

        return cur_tour, next_tour

    def get_cur_tour_info(self, league_name: str) -> Optional[Dict[str, Any]]:
        if league_name not in self.__leagues:
            logging.info(f"Wrong league_name={league_name} in get_deadline")
            return None

        cur_tour, next_tour = self.__get_current_tour(self.__leagues[league_name])
        if cur_tour is not None:
            result = {
                "number": int(cur_tour["name"].split(" ")[0]),
                "matches_count": len(cur_tour["matches"]),
                "deadline": iso8601.parse_date(cur_tour["startedAt"]).replace(
                    tzinfo=pytz.UTC
                ),
            }
            if next_tour is not None:
                result["next_tour_deadline"] = iso8601.parse_date(
                    next_tour["startedAt"]
                ).replace(tzinfo=pytz.UTC)
            return result
        else:
            return None

    def get_tour_transfers(self, squad_id: int) -> Optional[bool]:
        data = self.__request_for_squad_id(squad_id, "squad")
        if data is None:
            return None

        query_id = data["data"].keys()[0]
        tour = data["data"][query_id]["squads"][0]["currentTourInfo"]["tour"]
        all_transfers = tour["constraints"]["totalTransfers"]
        transfers_left = tour["transfersLeft"]

        return all_transfers != transfers_left
