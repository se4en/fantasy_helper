import typing as t
import os
from datetime import datetime
import logging
import json

import requests
import iso8601


class SportsParser:
    def __init__(
        self,
        url: str = "https://www.sports.ru/gql/graphql/",
        queries_path: t.Optional[str] = None,
    ):
        self.__url = url
        if queries_path is not None:
            self.__queries_path = queries_path
        else:
            self.__queries_path = os.path.join(os.path.dirname(__file__), "/queries")
        self.leagues = {  # TODO init from config
            "Russia": 2517,
            # "England": "https://1xstavka.ru/line/Football/88637-England-Premier-League/",
            # "France": "https://1xstavka.ru/line/Football/12821-France-Ligue-1/",
            # "Germany": "https://1xstavka.ru/line/Football/96463-Germany-Bundesliga/",
            # "Spain": "https://1xstavka.ru/line/Football/127733-Spain-La-Liga/",
            # "Netherlands": "https://1xstavka.ru/line/Football/2018750-Netherlands-Eredivisie/",
            # "Championship": "https://1xstavka.ru/line/Football/105759-England-Championship/",
            # "Turkey": "https://1xstavka.ru/line/Football/11113-Turkey-SuperLiga/",
            # "Italy": "https://1xstavka.ru/line/Football/110163-Italy-Serie-A/",
            # "Portugal": "https://1xstavka.ru/line/Football/118663-Portugal-Primeira-Liga/",
            # "UEFA_1": "https://1xstavka.ru/line/Football/118587-UEFA-Champions-League/",
            # "UEFA_2": "https://1xstavka.ru/line/Football/118593-UEFA-Europa-League/",
        }

    def __get_query_body(
        self, query_name: t.Literal["squad", "tournament"]
    ) -> t.Optional[str]:
        fname = os.path.join(self.__queries_path, f"{query_name}.graphql")

        if os.path.exists(fname):
            with open(fname, "r") as f:
                return f.read()
        else:
            # TODO log incorrect query file name
            return None

    def __request_for_squad_id(
        self, squad_id: int, query_name: t.Literal["squad", "tournament"]
    ) -> t.Optional[dict]:
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

    def __get_current_tour(self, squad_id: int) -> t.Optional[dict]:
        data = self.__request_for_squad_id(squad_id, "tournament")
        if data is None:
            return None

        # looking for current tour
        query_id = data["data"].keys()[0]
        for tour in data["data"][query_id]["squads"][0]["season"]["tours"]:
            if tour["status"] == "OPENED":
                break

        return tour

    def get_tour_deadline(self, league_name: str) -> t.Optional[datetime]:
        if league_name not in self.leagues:
            logging.info(f"Wrong league_name={league_name} in get_deadline")
            return None

        tour = self.__get_current_tour(self.leagues[league_name])
        if tour is not None:
            return iso8601.parse_date(tour["startedAt"])
        else:
            return None

    def get_tour_games_count(self, league_name: str) -> t.Optional[int]:
        if league_name not in self.leagues:
            logging.info(f"Wrong league_name={league_name} in get_deadline")
            return None

        tour = self.__get_current_tour(self.leagues[league_name])
        if tour is not None:
            return len(tour["matches"])
        else:
            return None

    def get_tour_transfers(self, squad_id: int) -> t.Optional[bool]:
        data = self.__request_for_squad_id(squad_id, "squad")
        if data is None:
            return None

        query_id = data["data"].keys()[0]
        tour = data["data"][query_id]["squads"][0]["currentTourInfo"]["tour"]
        all_transfers = tour["constraints"]["totalTransfers"]
        transfers_left = tour["transfersLeft"]

        return all_transfers != transfers_left
