"""Chargement du fichier préparé et vérification du contrat de données.

Le contrat est décrit dans docs/data_dictionary.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

PROCESSED_PATH = Path("data/processed/articles.parquet")
DEMO_PATH = Path("data/processed/demo.parquet")

REQUIRED_COLUMNS = [
    "id",
    "title",
    "abstract",
    "authors",
    "submitted_at",
    "year",
    "categories",
    "selected_categories",
    "arxiv_url",
]
TEXT_COLUMNS = ["title", "abstract", "authors"]
LIST_COLUMNS = ["categories", "selected_categories"]


class DataError(Exception):
    """Le fichier de données est absent ou ne respecte pas le contrat."""


@dataclass(frozen=True)
class DataSource:
    path: Path
    # Vrai quand le fichier vient des données fictives de data/sample/.
    is_demo: bool


def find_source(root: Path = Path(".")) -> DataSource:
    """Choisit le fichier préparé s'il existe, sinon la démonstration fictive."""
    processed = root / PROCESSED_PATH
    if processed.exists():
        return DataSource(processed, is_demo=False)
    demo = root / DEMO_PATH
    if demo.exists():
        return DataSource(demo, is_demo=True)
    raise DataError(
        f"Aucun fichier de données trouvé : ni {PROCESSED_PATH} ni {DEMO_PATH}. "
        "Lancez la commande de préparation du README (section « Préparer les vraies "
        "données » ou « Essayer sans télécharger Kaggle »), puis rechargez la page."
    )


def validate(articles: pd.DataFrame) -> None:
    """Vérifie les règles du contrat dont dépend l'interface."""
    missing = [column for column in REQUIRED_COLUMNS if column not in articles.columns]
    if missing:
        raise DataError(
            "Le fichier de données ne respecte pas le contrat (docs/data_dictionary.md). "
            "Colonnes manquantes : " + ", ".join(missing)
        )
    if articles["id"].duplicated().any():
        raise DataError(
            "Le fichier de données contient des identifiants en double : "
            "un article doit apparaître une seule fois."
        )


def load_articles(path: Path) -> pd.DataFrame:
    """Lit le fichier Parquet et renvoie une table conforme au contrat."""
    try:
        articles = pd.read_parquet(path)
    except Exception as error:  # fichier illisible ou corrompu
        raise DataError(f"Impossible de lire {path} : {error}") from error
    validate(articles)
    # Les listes Parquet arrivent en tableaux NumPy : on les fige en tuples.
    for column in LIST_COLUMNS:
        articles[column] = articles[column].map(
            lambda values: tuple(values) if values is not None else ()
        )
    for column in TEXT_COLUMNS:
        articles[column] = articles[column].fillna("")
    return articles
