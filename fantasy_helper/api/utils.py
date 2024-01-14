from typing import List

from fantasy_helper.utils.dataclasses import MatchInfo


def get_stat_from_mathes(
    cur_tour_matches: List[MatchInfo], next_tour_matches: List[MatchInfo]
) -> dict:
    unique_teams = set(
        [match.home_team for match in cur_tour_matches + next_tour_matches]
        + [match.away_team for match in cur_tour_matches + next_tour_matches]
    )
    result = {team_name: {} for team_name in unique_teams}

    for matches, tour_type in zip(
        (cur_tour_matches, next_tour_matches), ("cur", "next")
    ):
        for match in matches:
            result[match.home_team][f"{tour_type}_vs_name"] = match.away_team + " [д]"
            # result[match.home_team][f"{tour_type}_vs_loc"] = ""
            result[match.home_team][f"{tour_type}_attack"] = match.total_1_over_1_5
            result[match.home_team][f"{tour_type}_defend"] = match.total_2_under_0_5

            result[match.away_team][f"{tour_type}_vs_name"] = match.home_team + " [г]"
            # result[match.away_team][f"{tour_type}_vs_loc"] = "away"
            result[match.away_team][f"{tour_type}_attack"] = match.total_2_over_1_5
            result[match.away_team][f"{tour_type}_defend"] = match.total_1_under_0_5

    return result
