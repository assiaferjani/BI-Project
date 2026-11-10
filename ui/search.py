"""Recherche textuelle dans les titres et les résumés."""

from __future__ import annotations

import pandas as pd

SEARCH_COLUMNS = ["title", "abstract"]


def clean_query(query: str) -> str:
    """Retire les espaces en trop ; les textes préparés ont déjà des espaces simples."""
    return " ".join(query.split())


def matches(articles: pd.DataFrame, query: str) -> pd.Series:
    """Lignes dont le titre ou le résumé contient l'expression saisie.

    L'expression est prise telle quelle (pas d'expression régulière), sans
    tenir compte des majuscules : la ponctuation saisie ne peut pas provoquer
    d'erreur. Une recherche vide garde toutes les lignes.
    """
    needle = clean_query(query)
    found = pd.Series(not needle, index=articles.index)
    if needle:
        for column in SEARCH_COLUMNS:
            found |= articles[column].str.contains(needle, case=False, regex=False)
    return found
