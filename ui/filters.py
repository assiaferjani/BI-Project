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
    # Aucune catégorie sélectionnée signifie « toutes ».
    categories: tuple[str, ...] = ()


def year_bounds(articles: pd.DataFrame) -> tuple[int, int]:
    """Première et dernière année de premier dépôt présentes dans les données."""
    return int(articles["year"].min()), int(articles["year"].max())


def available_categories(articles: pd.DataFrame) -> list[str]:
    """Catégories étudiées présentes dans les données, par ordre alphabétique."""
    return sorted({code for codes in articles["selected_categories"] for code in codes})


def apply_filters(articles: pd.DataFrame, filters: Filters) -> pd.DataFrame:
    """Renvoie les articles qui respectent tous les filtres.

    Les bornes d'années sont incluses. Avec plusieurs catégories sélectionnées,
    un article est retenu si au moins une de ses catégories est sélectionnée.
    """
    keep = articles["year"].between(filters.year_min, filters.year_max)
    if filters.categories:
        chosen = set(filters.categories)
        keep &= articles["selected_categories"].map(lambda codes: not chosen.isdisjoint(codes))
    return articles[keep]
