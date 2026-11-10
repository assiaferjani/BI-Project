"""Filtres communs à tous les écrans.

Les filtres sont appliqués une seule fois ; les cartes, les graphiques, la
liste et l'export partent tous de la table renvoyée par apply_filters.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Filters:
    year_min: int
    year_max: int
    # Aucune famille sélectionnée signifie « toutes ».
    genres: tuple[str, ...] = ()


def year_bounds(tracks: pd.DataFrame) -> tuple[int, int]:
    """Première et dernière année présentes dans les données."""
    return int(tracks["year"].min()), int(tracks["year"].max())


def available_genres(tracks: pd.DataFrame) -> list[str]:
    """Familles de genres présentes dans les données, par ordre alphabétique."""
    return sorted({genre for genres in tracks["selected_genres"] for genre in genres})


def apply_filters(tracks: pd.DataFrame, filters: Filters) -> pd.DataFrame:
    """Renvoie les titres qui respectent tous les filtres.

    Les bornes d'années sont incluses. Avec plusieurs familles sélectionnées,
    un titre est retenu si au moins une de ses familles est sélectionnée.
    """
    keep = tracks["year"].between(filters.year_min, filters.year_max)
    if filters.genres:
        chosen = set(filters.genres)
        keep &= tracks["selected_genres"].map(lambda genres: not chosen.isdisjoint(genres))
    return tracks[keep]
