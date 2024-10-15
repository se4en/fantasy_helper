from typing import Optional

import numpy as np
import pandas as pd
import streamlit as st

from fantasy_helper.utils.dataclasses import SportsPlayerDiff


def rename_sports_role(role: str) -> Optional[str]:
    return {
        "GOALKEEPER": "вр",
        "DEFENDER": "зщ",
        "MIDFIELDER": "пз",
        "FORWARD": "нп",
    }.get(role)


def color_popularity(
    val: float, q_1: float, q_2: float, q_3: float, q_4: float
) -> str:
    if pd.isna(val):
        return ""
    elif val <= q_1:
        color = "#E06456"
    elif val <= q_2:
        color = "#EBA654" # "#E57878"
    elif val >= q_4:
        color = "#85DE6F"
    elif val >= q_3:
        color = "#EBE054" # "#85DE6F"
    else:
        return ""

    return f"background-color: {color}"


def plot_sports_players(players: SportsPlayerDiff, team_name: str = "All") -> None:
    df = pd.DataFrame([player.__dict__ for player in players])
    if df is None or len(df) == 0:
        return

    df.drop(columns=["league_name"], inplace=True, errors="ignore")
    df["role"] = df["role"].apply(rename_sports_role)

    if team_name != "All":
        df = df.loc[df["team_name"] == team_name]
    df.dropna(axis=1, how="all", inplace=True)
    df.fillna(0, inplace=True)
    df = df.rename(columns={
        "name": "Имя",
        "team_name": "Команда",
        "role": "Позиция",
        "price": "Цена",
        "percent_ownership": "Популярность",
        "percent_ownership_diff": "Динамика",
    })

    q1 = np.percentile(df["Динамика"], q=1)
    q2 = np.percentile(df["Динамика"], q=5)
    q3 = np.percentile(df["Динамика"], q=95)
    q4 = np.percentile(df["Динамика"], q=99)

    st.dataframe(
        df.style.format("{:.2f}", subset=["Популярность", "Динамика"])
        .format("{:.1f}", subset=["Цена"])
        .map(lambda x: color_popularity(x, q1, q2, q3, q4), subset=["Динамика"]),
        hide_index=True
    )
