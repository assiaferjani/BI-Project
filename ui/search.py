"""Recherche textuelle dans les titres et les noms d'artistes."""

from __future__ import annotations

import unicodedata

import pandas as pd

SEARCH_COLUMN = "search_text"


def normalize(text: str) -> str:
    """Met le texte sous une forme comparable : sans accents, sans casse, espaces réduits."""
    decomposed = unicodedata.normalize("NFKD", text)
    without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(without_accents.casefold().split())


def add_search_column(tracks: pd.DataFrame) -> pd.DataFrame:
    """Ajoute le texte de recherche : titre suivi des noms d'artistes, normalisés."""
    text = tracks["name"].fillna("") + " " + tracks["artists"].map(" ".join)
    tracks[SEARCH_COLUMN] = text.map(normalize)
    return tracks


def matches(tracks: pd.DataFrame, query: str) -> pd.Series:
    """Lignes dont le titre ou les artistes contiennent l'expression saisie.

    L'expression est prise telle quelle (pas d'expression régulière) : la
    ponctuation saisie ne peut pas provoquer d'erreur. Une recherche vide
    garde toutes les lignes.
    """
    needle = normalize(query)
    if not needle:
        return pd.Series(True, index=tracks.index)
    return tracks[SEARCH_COLUMN].str.contains(needle, regex=False)
