from typing import List, Tuple, Optional

import pandas as pd
import matplotlib as mpl
from mplsoccer import VerticalPitch, Sbopen, FontManager, inset_image

from fantasy_helper.utils.dataclasses import MatchInfo


def position_to_id(position: str) -> int:
    position_mapping = {
        "GK": 1,
        "RB": 2,
        "RCB": 3,
        "CB": 4,
        "LCB": 5,
        "LB": 6,
        "RWB": 7,
        "LWB": 8,
        "RDM": 9,
        "CDM": 10,
        "LDM": 11,
        "RM": 12,
        "RCM": 13,
        "CM": 14,
        "LCM": 15,
        "LM": 16,
        "RW": 17,
        "RAM": 18,
        "CAM": 19,
        "LAM": 20,
        "LW": 21,
        "RCF": 22,
        "ST": 23,
        "LCF": 24,
        "SS": 25,
    }
    return position_mapping.get(position, 0)


def zones_to_formation(zones_players: List[List[str]]) -> str:
    result = ""
    for zone_players in zones_players[1:]:
        result += str(len(zone_players))

    return result


def prepare_name(name: str) -> str:
    return name


def pose_433(zones_players: List[List[str]]) -> Tuple[List[int], List[str]]:
    positions, names = [position_to_id("GK")], [prepare_name(zones_players[0][0])]

    # add defenders
    for position, name in zip(["RB", "RCB", "LCB", "LB"], zones_players[1]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add midfielders
    for position, name in zip(["RCM", "CDM", "LCM"], zones_players[2]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add attackers
    for position, name in zip(["RW", "ST", "LW"], zones_players[3]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    return positions, names


def pose_4321(zones_players: List[List[str]]) -> Tuple[List[int], List[str]]:
    positions, names = [position_to_id("GK")], [prepare_name(zones_players[0][0])]

    # add defenders
    for position, name in zip(["RB", "RCB", "LCB", "LB"], zones_players[1]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add midfielders
    for position, name in zip(["RCM", "CM", "LCM"], zones_players[2]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add attackers
    for position, name in zip(["RW", "LW"], zones_players[3]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add attackers
    for position, name in zip(["ST"], zones_players[4]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    return positions, names


def pose_442(zones_players: List[List[str]]) -> Tuple[List[int], List[str]]:
    positions, names = [position_to_id("GK")], [prepare_name(zones_players[0][0])]

    # add defenders
    for position, name in zip(["RB", "RCB", "LCB", "LB"], zones_players[1]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add midfielders
    for position, name in zip(["RM", "RCM", "LCM", "LM"], zones_players[2]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add attackers
    for position, name in zip(["RCF", "LCF"], zones_players[3]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    return positions, names


def pose_4231(zones_players: List[List[str]]) -> Tuple[List[int], List[str]]:
    positions, names = [position_to_id("GK")], [prepare_name(zones_players[0][0])]

    # add defenders
    for position, name in zip(["RB", "RCB", "LCB", "LB"], zones_players[1]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add defend midfielders
    for position, name in zip(["RDM", "LDM"], zones_players[2]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add attack midfielders
    for position, name in zip(["RW", "CAM", "LW"], zones_players[3]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add attackers
    for position, name in zip(["ST"], zones_players[4]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    return positions, names


def pose_4141(zones_players: List[List[str]]) -> Tuple[List[int], List[str]]:
    positions, names = [position_to_id("GK")], [prepare_name(zones_players[0][0])]

    # add defenders
    for position, name in zip(["RB", "RCB", "LCB", "LB"], zones_players[1]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add defend midfielders
    for position, name in zip(["CDM"], zones_players[2]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add attack midfielders
    for position, name in zip(["RM", "RCM", "LCM", "LM"], zones_players[3]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add attackers
    for position, name in zip(["ST"], zones_players[4]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    return positions, names


def pose_4222(zones_players: List[List[str]]) -> Tuple[List[int], List[str]]:
    positions, names = [position_to_id("GK")], [prepare_name(zones_players[0][0])]

    # add defenders
    for position, name in zip(["RB", "RCB", "LCB", "LB"], zones_players[1]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add defend midfielders
    for position, name in zip(["RDM", "LDM"], zones_players[2]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add attack midfielders
    for position, name in zip(["RM", "LM"], zones_players[3]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add attackers
    for position, name in zip(["RCF", "LCF"], zones_players[4]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    return positions, names


def pose_352(zones_players: List[List[str]]) -> Tuple[List[int], List[str]]:
    positions, names = [position_to_id("GK")], [prepare_name(zones_players[0][0])]

    # add defenders
    for position, name in zip(["RCB", "CB", "LCB"], zones_players[1]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add midfielders
    for position, name in zip(["RWB", "RCM", "CM", "LCM", "LWB"], zones_players[2]):
        print(position, position_to_id(position), name)
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add attackers
    for position, name in zip(["RCF", "LCF"], zones_players[3]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    return positions, names


def pose_532(zones_players: List[List[str]]) -> Tuple[List[int], List[str]]:
    positions, names = [position_to_id("GK")], [prepare_name(zones_players[0][0])]

    # add defenders
    for position, name in zip(["RB", "RCB", "CB", "LCB", "LB"], zones_players[1]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add midfielders
    for position, name in zip(["RCM", "CDM", "LCM"], zones_players[2]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add attackers
    for position, name in zip(["RCF", "LCF"], zones_players[3]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    return positions, names


def pose_343(zones_players: List[List[str]]) -> Tuple[List[int], List[str]]:
    positions, names = [position_to_id("GK")], [prepare_name(zones_players[0][0])]

    # add defenders
    for position, name in zip(["RCB", "CB", "LCB"], zones_players[1]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add midfielders
    for position, name in zip(["RWB", "RCM", "LCM", "LWB"], zones_players[2]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add attackers
    for position, name in zip(["RW", "ST", "LW"], zones_players[3]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    return positions, names


def pose_3421(zones_players: List[List[str]]) -> Tuple[List[int], List[str]]:
    positions, names = [position_to_id("GK")], [prepare_name(zones_players[0][0])]

    # add defenders
    for position, name in zip(["RCB", "CB", "LCB"], zones_players[1]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add midfielders
    for position, name in zip(["RWB", "RDM", "LDM", "LWB"], zones_players[2]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add attackers
    for position, name in zip(["RAM", "LAM"], zones_players[3]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add attackers
    for position, name in zip(["ST"], zones_players[3]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    return positions, names


def pose_41212(zones_players: List[List[str]]) -> Tuple[List[int], List[str]]:
    positions, names = [position_to_id("GK")], [prepare_name(zones_players[0][0])]

    # add defenders
    for position, name in zip(["RWB", "RCB", "CB", "LCB", "LWB"], zones_players[1]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add midfielder
    for position, name in zip(["CDM"], zones_players[2]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add midfielders
    for position, name in zip(["RCM", "LCM"], zones_players[3]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add midfielder
    for position, name in zip(["CAM"], zones_players[4]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add attackers
    for position, name in zip(["RCF", "LCF"], zones_players[5]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    return positions, names


def pose_451(zones_players: List[List[str]]) -> Tuple[List[int], List[str]]:
    positions, names = [position_to_id("GK")], [prepare_name(zones_players[0][0])]

    # add defenders
    for position, name in zip(["RB", "RCB", "LCB", "LB"], zones_players[1]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add midfielders
    for position, name in zip(["RM", "RCM", "CM", "LCM", "LM"], zones_players[2]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add attackers
    for position, name in zip(["ST"], zones_players[3]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    return positions, names


def pose_4411(zones_players: List[List[str]]) -> Tuple[List[int], List[str]]:
    positions, names = [position_to_id("GK")], [prepare_name(zones_players[0][0])]

    # add defenders
    for position, name in zip(["RB", "RCB", "LCB", "LB"], zones_players[1]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add midfielders
    for position, name in zip(["RM", "RCM", "LCM", "LM"], zones_players[2]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add midfielder
    for position, name in zip(["CAM"], zones_players[3]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add attackers
    for position, name in zip(["ST"], zones_players[4]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    return positions, names


def pose_541(zones_players: List[List[str]]) -> Tuple[List[int], List[str]]:
    positions, names = [position_to_id("GK")], [prepare_name(zones_players[0][0])]

    # add defenders
    for position, name in zip(["RWB", "RCB", "CB", "LCB", "LWB"], zones_players[1]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add midfielders
    for position, name in zip(["RM", "RCM", "LCM", "LM"], zones_players[2]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add attacker
    for position, name in zip(["ST"], zones_players[3]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    return positions, names


def pose_31312(zones_players: List[List[str]]) -> Tuple[List[int], List[str]]:
    positions, names = [position_to_id("GK")], [prepare_name(zones_players[0][0])]

    # add defenders
    for position, name in zip(["RCB", "CB", "LCB"], zones_players[1]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add midfielder
    for position, name in zip(["CDM"], zones_players[2]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add midfielders
    for position, name in zip(["RCM", "CM", "LCM"], zones_players[3]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add midfielder
    for position, name in zip(["SS"], zones_players[4]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add attackers
    for position, name in zip(["RCF", "LCF"], zones_players[5]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    return positions, names


def pose_3511(zones_players: List[List[str]]) -> Tuple[List[int], List[str]]:
    positions, names = [position_to_id("GK")], [prepare_name(zones_players[0][0])]

    # add defenders
    for position, name in zip(["RCB", "CB", "LCB"], zones_players[1]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add midfielders
    for position, name in zip(["RWB", "RCM", "CDM", "LCM", "LWB"], zones_players[2]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add midfielder
    for position, name in zip(["CAM"], zones_players[3]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add attacker
    for position, name in zip(["ST"], zones_players[4]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    return positions, names


def pose_3412(zones_players: List[List[str]]) -> Tuple[List[int], List[str]]:
    positions, names = [position_to_id("GK")], [prepare_name(zones_players[0][0])]

    # add defenders
    for position, name in zip(["RCB", "CB", "LCB"], zones_players[1]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add midfielders
    for position, name in zip(["RWB", "RCM", "LCM", "LWB"], zones_players[2]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add midfielder
    for position, name in zip(["CAM"], zones_players[3]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add attackers
    for position, name in zip(["RCF", "LCF"], zones_players[4]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    return positions, names


def pose_3142(zones_players: List[List[str]]) -> Tuple[List[int], List[str]]:
    positions, names = [position_to_id("GK")], [prepare_name(zones_players[0][0])]

    # add defenders
    for position, name in zip(["RCB", "CB", "LCB"], zones_players[1]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add midfielder
    for position, name in zip(["CDM"], zones_players[2]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add midfielders
    for position, name in zip(["RM", "RCM", "LCM", "LM"], zones_players[3]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add attackers
    for position, name in zip(["RCF", "LCF"], zones_players[4]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    return positions, names


def pose_4132(zones_players: List[List[str]]) -> Tuple[List[int], List[str]]:
    positions, names = [position_to_id("GK")], [prepare_name(zones_players[0][0])]

    # add defenders
    for position, name in zip(["RB", "RCB", "LCB", "LB"], zones_players[1]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add midfielder
    for position, name in zip(["CDM"], zones_players[2]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add midfielders
    for position, name in zip(["RW", "CAM", "LW"], zones_players[3]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    # add attackers
    for position, name in zip(["RCF", "LCF"], zones_players[4]):
        positions.append(position_to_id(position))
        names.append(prepare_name(name))

    return positions, names


def lineup_to_formation(lineup: str) -> Tuple[str, List[int], List[str]]:
    zones = list(map(lambda x: x.strip(), lineup.split(";")))
    zones_players = [
        [player.strip() for player in players.split(",")] for players in zones
    ]
    formation = zones_to_formation(zones_players)

    if (
        len(zones_players) == 4
        and len(zones_players[0]) == 1
        and len(zones_players[1]) == 4
        and len(zones_players[2]) == 3
        and len(zones_players[3]) == 3
    ):
        positions, names = pose_433(zones_players)
    elif (
        len(zones_players) == 5
        and len(zones_players[0]) == 1
        and len(zones_players[1]) == 4
        and len(zones_players[2]) == 3
        and len(zones_players[3]) == 2
        and len(zones_players[4]) == 1
    ):
        positions, names = pose_4321(zones_players)
    elif (
        len(zones_players) == 5
        and len(zones_players[0]) == 1
        and len(zones_players[1]) == 4
        and len(zones_players[2]) == 1
        and len(zones_players[3]) == 4
        and len(zones_players[4]) == 1
    ):
        positions, names = pose_4141(zones_players)
    elif (
        len(zones_players) == 5
        and len(zones_players[0]) == 1
        and len(zones_players[1]) == 4
        and len(zones_players[2]) == 2
        and len(zones_players[3]) == 2
        and len(zones_players[4]) == 2
    ):
        positions, names = pose_4222(zones_players)
    elif (
        len(zones_players) == 4
        and len(zones_players[0]) == 1
        and len(zones_players[1]) == 4
        and len(zones_players[2]) == 4
        and len(zones_players[3]) == 2
    ):
        positions, names = pose_442(zones_players)
    elif (
        len(zones_players) == 5
        and len(zones_players[0]) == 1
        and len(zones_players[1]) == 4
        and len(zones_players[2]) == 2
        and len(zones_players[3]) == 3
        and len(zones_players[4]) == 1
    ):
        positions, names = pose_4231(zones_players)
    elif (
        len(zones_players) == 4
        and len(zones_players[0]) == 1
        and len(zones_players[1]) == 3
        and len(zones_players[2]) == 5
        and len(zones_players[3]) == 2
    ):
        positions, names = pose_352(zones_players)
    elif (
        len(zones_players) == 4
        and len(zones_players[0]) == 1
        and len(zones_players[1]) == 5
        and len(zones_players[2]) == 3
        and len(zones_players[3]) == 2
    ):
        positions, names = pose_532(zones_players)
    elif (
        len(zones_players) == 4
        and len(zones_players[0]) == 1
        and len(zones_players[1]) == 3
        and len(zones_players[2]) == 4
        and len(zones_players[3]) == 3
    ):
        positions, names = pose_343(zones_players)
    elif (
        len(zones_players) == 5
        and len(zones_players[0]) == 1
        and len(zones_players[1]) == 3
        and len(zones_players[2]) == 4
        and len(zones_players[3]) == 2
        and len(zones_players[4]) == 1
    ):
        positions, names = pose_3421(zones_players)
    elif (
        len(zones_players) == 6
        and len(zones_players[0]) == 1
        and len(zones_players[1]) == 4
        and len(zones_players[2]) == 1
        and len(zones_players[3]) == 2
        and len(zones_players[4]) == 1
        and len(zones_players[5]) == 2
    ):
        positions, names = pose_41212(zones_players)
    elif (
        len(zones_players) == 4
        and len(zones_players[0]) == 1
        and len(zones_players[1]) == 4
        and len(zones_players[2]) == 5
        and len(zones_players[3]) == 1
    ):
        positions, names = pose_451(zones_players)
    elif (
        len(zones_players) == 5
        and len(zones_players[0]) == 1
        and len(zones_players[1]) == 4
        and len(zones_players[2]) == 4
        and len(zones_players[3]) == 1
        and len(zones_players[4]) == 1
    ):
        positions, names = pose_4411(zones_players)
    elif (
        len(zones_players) == 4
        and len(zones_players[0]) == 1
        and len(zones_players[1]) == 5
        and len(zones_players[2]) == 4
        and len(zones_players[3]) == 1
    ):
        positions, names = pose_541(zones_players)
    elif (
        len(zones_players) == 6
        and len(zones_players[0]) == 1
        and len(zones_players[1]) == 3
        and len(zones_players[2]) == 1
        and len(zones_players[3]) == 3
        and len(zones_players[4]) == 1
        and len(zones_players[5]) == 2
    ):
        positions, names = pose_31312(zones_players)
    elif (
        len(zones_players) == 5
        and len(zones_players[0]) == 1
        and len(zones_players[1]) == 3
        and len(zones_players[2]) == 5
        and len(zones_players[3]) == 1
        and len(zones_players[4]) == 1
    ):
        positions, names = pose_3511(zones_players)
    elif (
        len(zones_players) == 5
        and len(zones_players[0]) == 1
        and len(zones_players[1]) == 3
        and len(zones_players[2]) == 4
        and len(zones_players[3]) == 1
        and len(zones_players[4]) == 2
    ):
        positions, names = pose_3412(zones_players)
    elif (
        len(zones_players) == 5
        and len(zones_players[0]) == 1
        and len(zones_players[1]) == 3
        and len(zones_players[2]) == 1
        and len(zones_players[3]) == 4
        and len(zones_players[4]) == 2
    ):
        positions, names = pose_3142(zones_players)
    elif (
        len(zones_players) == 5
        and len(zones_players[0]) == 1
        and len(zones_players[1]) == 4
        and len(zones_players[2]) == 1
        and len(zones_players[3]) == 3
        and len(zones_players[4]) == 2
    ):
        positions, names = pose_4132(zones_players)
    else:
        positions, names = [], []

    return formation, positions, names


def plot_lineup(formation, positions, names):
    pitch = VerticalPitch(goal_type="box")
    fig, ax = pitch.draw(figsize=(6, 8.72))
    ax_text = pitch.formation(
        formation,
        positions=positions,
        kind="text",
        text=names,
        va="center",
        ha="center",
        fontsize=16,
        ax=ax,
    )
    # scatter markers
    mpl.rcParams["hatch.linewidth"] = 3
    mpl.rcParams["hatch.color"] = "#95A5A6"
    ax_scatter = pitch.formation(
        formation,
        positions=positions,
        kind="scatter",
        c="#2E4053",
        hatch="||",
        linewidth=3,
        s=500,
        xoffset=-8,
        ax=ax,
    )

    return fig


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


def color_coeff(
    val: float, th_0: float = 1.5, th_1: float = 2.0, th_2: float = 3.0
) -> str:
    if pd.isna(val):
        return ""
    elif val <= th_0:
        color = "#85DE6F"
    elif val <= th_1:
        color = "#EBE054"
    elif val <= th_2:
        color = "#EBA654"
    else:
        color = "#E06456"

    return f"background-color: {color}"


if __name__ == "__main__":
    formation, positions, names = lineup_to_formation(lineup)
    print(formation)
    print(positions)
    print(names)
