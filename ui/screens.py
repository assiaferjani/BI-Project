"""Contenu des quatre onglets de l'application."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from ui.data import DataSource
from ui.filters import Filters, available_genres

MAX_ROWS = 50
SOURCE_URL = "https://www.kaggle.com/datasets/yamaerenay/spotify-dataset-19212020-600k-tracks"
EMPTY_MESSAGE = (
    "Aucun titre ne correspond à ces filtres. Élargissez la période ou "
    "retirez une famille de genres."
)


def format_count(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def overview(filtered: pd.DataFrame, filters: Filters) -> None:
    total = filtered["id"].nunique()
    genres = available_genres(filtered)
    left, middle, right = st.columns(3)
    left.metric("Titres uniques", format_count(total))
    middle.metric("Période filtrée", f"{filters.year_min} à {filters.year_max}")
    right.metric("Familles de genres", len(genres))
    if total == 0:
        st.warning(EMPTY_MESSAGE)
        return
    st.caption(
        "Un titre est compté une seule fois, même s'il appartient à plusieurs familles."
    )


def comparison(filtered: pd.DataFrame) -> None:
    if filtered.empty:
        st.warning(EMPTY_MESSAGE)
        return
    st.caption(
        "Un titre peut appartenir à plusieurs familles : la somme des familles "
        "dépasse le nombre de titres uniques."
    )


def exploration(filtered: pd.DataFrame) -> None:
    total = filtered["id"].nunique()
    if total == 0:
        st.warning(EMPTY_MESSAGE)
        return
    shown = filtered.sort_values(["popularity", "id"], ascending=[False, True]).head(MAX_ROWS)
    st.write(
        f"{format_count(total)} titres correspondent aux filtres ; "
        f"les {len(shown)} plus populaires sont affichés."
    )
    table = pd.DataFrame(
        {
            "Titre": shown["name"].where(shown["name"] != "", "(sans titre)"),
            "Artistes": shown["artists"].map(", ".join),
            "Année": shown["year"],
            "Familles": shown["selected_genres"].map(", ".join),
            "Popularité": shown["popularity"],
            "Lien": shown["spotify_url"],
        }
    )
    st.dataframe(
        table,
        hide_index=True,
        width="stretch",
        column_config={
            "Année": st.column_config.NumberColumn(format="%d"),
            "Lien": st.column_config.LinkColumn(display_text="Ouvrir dans Spotify"),
        },
    )


def method(tracks: pd.DataFrame, source: DataSource) -> None:
    first_year, last_year = int(tracks["year"].min()), int(tracks["year"].max())
    st.markdown(
        f"""
**Source.** Kaggle, « Spotify Dataset 1921-2020, 600k+ Tracks » : [{SOURCE_URL}]({SOURCE_URL}).
Fichiers utilisés : `tracks.csv` et `artists.csv`.

**Fichier chargé.** `{source.path}`, {format_count(tracks["id"].nunique())} titres,
années {first_year} à {last_year}, familles : {", ".join(available_genres(tracks))}.

**Règles.**
- Un titre est identifié par son `id` Spotify et compté une seule fois.
- L'année est celle de la date de sortie du titre.
- Les genres sont ceux des artistes du titre, regroupés en familles.
- Plusieurs familles sélectionnées : un titre est retenu si au moins une de ses
  familles est sélectionnée. Aucune famille sélectionnée signifie « toutes ».

**Limites.**
- La popularité est celle mesurée par Spotify au moment de la collecte, pas à
  la sortie du titre.
- Plus de titres dans une famille ne signifie ni une meilleure musique ni plus
  d'écoutes.
- Les genres décrivent les artistes, pas chaque titre.
- Le jeu de données n'est pas un échantillon représentatif du catalogue Spotify.
"""
    )
