from typing import List, Tuple, Optional

import pandas as pd
import matplotlib as mpl
import streamlit as st
from mplsoccer import VerticalPitch, Sbopen, FontManager, inset_image

from fantasy_helper.utils.dataclasses import MatchInfo, PlayersLeagueStats


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
    for position, name in zip(["ST"], zones_players[4]):
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
    """
    Takes a lineup string and converts it into a formation.

    Args:
        lineup (str): The lineup string.

    Returns:
        Tuple[str, List[int], List[str]]: A tuple containing the formation string, the list of positions, and the list of player names.
    """
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


def plot_lineup(formation, positions, names) -> mpl.figure.Figure:
    """
    Generate a pitch lineup plot.

    Args:
        formation (str): The formation of the lineup.
        positions (list): The positions of the players.
        names (list): The names of the players.

    Returns:
        matplotlib.figure.Figure: The generated pitch lineup plot.
    """
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
    """
    Generate a dictionary containing statistical information for each team based on the given lists of current tour matches and next tour matches.

    Args:
        cur_tour_matches (List[MatchInfo]): A list of MatchInfo objects representing the matches in the current tour.
        next_tour_matches (List[MatchInfo]): A list of MatchInfo objects representing the matches in the next tour.

    Returns:
        dict: A dictionary with team names as keys and nested dictionaries as values. Each nested dictionary contains statistical information for the corresponding team, including the opponent's name in the current and next tour, attack and defense statistics for the current tour, and attack and defense statistics for the next tour.
    """
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
    """
    Calculate the color coefficient based on the input value.

    Args:
        val (float): The input value.
        th_0 (float, optional): The threshold for color category 0. Defaults to 1.5.
        th_1 (float, optional): The threshold for color category 1. Defaults to 2.0.
        th_2 (float, optional): The threshold for color category 2. Defaults to 3.0.

    Returns:
        str: The CSS background color based on the input value.
    """
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


def plot_coeff_df(df: pd.DataFrame):
    """
    Plot the coefficient dataframe.

    Args:
        df (pd.DataFrame): The dataframe containing the coefficient data.

    Returns:
        None
    """
    not_na_columns = df.columns[~df.isna().all()]
    attack_columns = list(filter(lambda x: x.startswith("Атака"), not_na_columns))
    defend_columns = list(filter(lambda x: x.startswith("Защита"), not_na_columns))

    st.dataframe(
        df.style.format("{:.3}", subset=attack_columns + defend_columns)
        .map(color_coeff, subset=attack_columns)
        .map(lambda x: color_coeff(x, 2.0, 2.5, 3.5), subset=defend_columns)
    )


def plot_main_players_stats(
    players_stats: PlayersLeagueStats,
    games_count: int,
    is_abs_stats: bool = True,
    min_minutes: Optional[int] = None,
    team_name: str = "All",
) -> None:
    """
    Plot the main players' stats based on the given parameters.

    Args:
        players_stats (PlayersLeagueStats): The object containing the players' league stats.
        games_count (int): The maximum number of games to consider.
        is_abs_stats (bool, optional): Flag indicating whether to use absolute stats or normalized stats. Defaults to True.
        min_minutes (Optional[int], optional): The minimum number of minutes played to consider. Defaults to None.
        team_name (str, optional): The name of the team to filter the stats for. Defaults to "All".

    Returns:
        None
    """
    if is_abs_stats:
        df = players_stats.abs_stats
    else:
        df = players_stats.norm_stats

    if df is None or len(df) == 0:
        return

    df.drop(columns=["id", "type", "league_name"], inplace=True, errors="ignore")

    if team_name != "All":
        df = df.loc[df["team"] == team_name]
    df = df.loc[df["games"] <= games_count]
    if min_minutes is not None:
        df = df.loc[df["minutes"] >= min_minutes]

    df.dropna(axis=1, how="all", inplace=True)

    def _get_max_game_count_row(group: pd.DataFrame) -> pd.DataFrame:
        """
        Get the row with the maximum game count from a given group.

        Args:
            group (pd.DataFrame): The group of data to search for the row with the maximum game count.

        Returns:
            pd.DataFrame: The row with the maximum game count, as a DataFrame. If no such row exists, an empty DataFrame is returned.
        """
        result = group.loc[group["games"] == group["games"].max()]
        if len(result) > 0:
            return pd.DataFrame(result.iloc[0].to_dict(), index=[0])
        else:
            return pd.DataFrame()

    if not df.empty:
        df = df.groupby(by=["name"]).apply(_get_max_game_count_row)
        df.reset_index(drop=True, inplace=True)
        df.fillna(0, inplace=True)

    st.dataframe(df)


def plot_free_kicks_stats(
    players_stats: PlayersLeagueStats, team_name: str = "All"
) -> None:
    """
    Generate a plot of free kicks statistics for players.

    Args:
        players_stats (PlayersLeagueStats): The players' league statistics.
        team_name (str, optional): The name of the team to filter the statistics for. Defaults to "All".

    Returns:
        None

    """
    df = players_stats.free_kicks

    if df is None or len(df) == 0:
        return

    df.drop(columns=["id", "type", "league_name"], inplace=True, errors="ignore")

    if team_name != "All":
        df = df.loc[df["team"] == team_name]
    df.dropna(axis=1, how="all", inplace=True)
    df.fillna(0, inplace=True)

    st.dataframe(df)


def centrize_header(text: str) -> None:
    """
    Centrize the header text by applying a CSS style to the Markdown content.

    Args:
        text (str): The text to be displayed as the header.

    Returns:
        None
    """
    style = "<style>h2 {text-align: center;}</style>"
    st.markdown(style, unsafe_allow_html=True)
    st.header(text)


if __name__ == "__main__":
    formation, positions, names = lineup_to_formation(lineup)
    print(formation)
    print(positions)
    print(names)
