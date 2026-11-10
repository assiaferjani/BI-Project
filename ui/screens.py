"""Contenu des quatre onglets de l'application."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from ui.data import DataSource
from ui.export import file_name, to_csv_bytes
from ui.filters import Filters, available_genres

PAGE_SIZE = 25
NO_TITLE = "(sans titre)"
FEATURE_LABELS = {
    "danceability": "Dansabilité (0 à 1)",
    "energy": "Énergie (0 à 1)",
    "valence": "Positivité (0 à 1)",
    "acousticness": "Acoustique (0 à 1)",
    "instrumentalness": "Instrumental (0 à 1)",
    "speechiness": "Présence de parole (0 à 1)",
    "liveness": "Enregistrement en public (0 à 1)",
    "loudness": "Volume sonore (dB)",
    "tempo": "Tempo (battements par minute)",
}
SOURCE_URL = "https://www.kaggle.com/datasets/yamaerenay/spotify-dataset-19212020-600k-tracks"
EMPTY_MESSAGE = (
    "Aucun titre ne correspond à ces filtres. Élargissez la période, retirez "
    "une famille de genres ou modifiez la recherche."
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


def display_name(name: str) -> str:
    return name if name else NO_TITLE


def format_duration(duration_ms: int) -> str:
    minutes, seconds = divmod(round(duration_ms / 1000), 60)
    return f"{minutes} min {seconds:02d} s"


def format_release(release_date: str, precision: str) -> str:
    note = {"year": " (année seule connue)", "month": " (mois connu, jour inconnu)"}
    return release_date + note.get(precision, "")


def page_count(total: int) -> int:
    return max(1, -(-total // PAGE_SIZE))


def track_label(track: pd.Series) -> str:
    return f"{display_name(track['name'])} · {', '.join(track['artists'])} ({track['year']})"


def track_detail(track: pd.Series) -> None:
    """Fiche d'un titre : informations générales puis caractéristiques audio."""
    with st.container(border=True):
        st.subheader(display_name(track["name"]))
        st.write(", ".join(track["artists"]) or "Artiste inconnu")
        left, right = st.columns(2)
        left.markdown(
            f"**Date de sortie :** {format_release(track['release_date'], track['release_precision'])}  \n"
            f"**Durée :** {format_duration(track['duration_ms'])}  \n"
            f"**Popularité :** {track['popularity']} / 100  \n"
            f"**Paroles explicites :** {'oui' if track['explicit'] else 'non'}"
        )
        right.markdown(
            f"**Familles :** {', '.join(track['selected_genres'])}  \n"
            f"**Genres des artistes :** {', '.join(track['genres']) or 'non renseignés'}"
        )
        features = pd.DataFrame(
            {
                "Caractéristique": [FEATURE_LABELS[name] for name in FEATURE_LABELS],
                "Valeur": [float(track[name]) for name in FEATURE_LABELS],
            }
        )
        st.dataframe(features, hide_index=True, width="stretch")
        st.link_button("Ouvrir dans Spotify", track["spotify_url"])


def exploration(filtered: pd.DataFrame, filters: Filters) -> None:
    total = filtered["id"].nunique()
    if total == 0:
        st.warning(EMPTY_MESSAGE)
        return

    ordered = filtered.sort_values(["popularity", "id"], ascending=[False, True])
    pages = page_count(total)
    summary, pager = st.columns([3, 1])
    page = 1
    if pages > 1:
        page = pager.number_input("Page", min_value=1, max_value=pages, value=1, key="page")
    start = (page - 1) * PAGE_SIZE
    shown = ordered.iloc[start : start + PAGE_SIZE]
    summary.write(
        f"{format_count(total)} titres correspondent aux filtres, classés par popularité. "
        f"Titres {start + 1} à {start + len(shown)}, page {page} sur {pages}."
    )

    table = pd.DataFrame(
        {
            "Titre": shown["name"].map(display_name),
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

    by_id = shown.set_index("id")
    chosen = st.selectbox(
        "Fiche d'un titre de cette page",
        options=list(by_id.index),
        format_func=lambda track_id: track_label(by_id.loc[track_id]),
        index=None,
        placeholder="Choisir un titre",
        key="detail",
    )
    if chosen is not None and chosen in by_id.index:
        track_detail(by_id.loc[chosen])

    st.download_button(
        f"Exporter les {format_count(total)} titres filtrés (CSV)",
        data=to_csv_bytes(filtered),
        file_name=file_name(filters),
        mime="text/csv",
        key="export",
    )
    st.caption(
        "L'export contient tous les titres filtrés, pas seulement la page affichée : "
        "une ligne par titre, listes séparées par « ; »."
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
- La recherche porte sur les titres et les noms d'artistes. Elle cherche
  l'expression exacte, sans tenir compte des majuscules ni des accents.
- L'export CSV contient exactement les titres filtrés, une ligne par titre.

**Limites.**
- La popularité est celle mesurée par Spotify au moment de la collecte, pas à
  la sortie du titre.
- Plus de titres dans une famille ne signifie ni une meilleure musique ni plus
  d'écoutes.
- Les genres décrivent les artistes, pas chaque titre.
- Le jeu de données n'est pas un échantillon représentatif du catalogue Spotify.
"""
    )
