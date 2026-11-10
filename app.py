"""Spotify Explorer : point d'entrée de l'application Streamlit.

Lancement : python -m streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from ui import screens
from ui.data import DataError, DataSource, find_source, load_tracks
from ui.filters import Filters, apply_filters, available_genres, year_bounds

st.set_page_config(page_title="Spotify Explorer", page_icon="🎧", layout="wide")


@st.cache_data(show_spinner="Chargement des titres…")
def cached_tracks(path: str, modified: float):
    # `modified` invalide le cache quand le fichier préparé est régénéré.
    return load_tracks(path)


def sidebar_filters(tracks) -> Filters:
    first_year, last_year = year_bounds(tracks)
    st.sidebar.header("Filtres")
    if first_year == last_year:
        years = (first_year, last_year)
        st.sidebar.write(f"Année : {first_year}")
    else:
        years = st.sidebar.slider(
            "Années de sortie",
            min_value=first_year,
            max_value=last_year,
            value=(first_year, last_year),
            key="years",
        )
    genres = st.sidebar.multiselect(
        "Familles de genres",
        options=available_genres(tracks),
        placeholder="Toutes les familles",
        help="Un titre est retenu si au moins une de ses familles est sélectionnée. "
        "Sans sélection, toutes les familles sont gardées.",
        key="genres",
    )
    return Filters(year_min=years[0], year_max=years[1], genres=tuple(genres))


def main() -> None:
    st.title("Spotify Explorer")
    st.caption(
        "Comment les titres Spotify évoluent-ils de 1960 à 2020 selon les familles de genres ?"
    )

    try:
        source: DataSource = find_source()
        tracks = cached_tracks(str(source.path), source.path.stat().st_mtime)
    except DataError as error:
        st.error(str(error))
        st.stop()

    if source.is_sample:
        st.warning(
            f"Données de démonstration : {len(tracks)} titres tirés au hasard. "
            "Les chiffres affichés ne sont pas des résultats. Préparez le fichier "
            "complet avec la commande du README pour voir les vraies valeurs."
        )

    filters = sidebar_filters(tracks)
    filtered = apply_filters(tracks, filters)

    overview_tab, comparison_tab, exploration_tab, method_tab = st.tabs(
        ["Vue d'ensemble", "Comparaison", "Exploration", "Méthode"]
    )
    with overview_tab:
        screens.overview(filtered, filters)
    with comparison_tab:
        screens.comparison(filtered)
    with exploration_tab:
        screens.exploration(filtered)
    with method_tab:
        screens.method(tracks, source)


main()
