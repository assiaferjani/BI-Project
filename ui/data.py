"""Chargement du fichier préparé et vérification du contrat de données."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

PROCESSED_PATH = Path("data/processed/tracks.parquet")
SAMPLE_PATH = Path("data/sample/tracks_sample.parquet")

AUDIO_FEATURES = [
    "danceability",
    "energy",
    "valence",
    "acousticness",
    "instrumentalness",
    "speechiness",
    "liveness",
    "loudness",
    "tempo",
]

# Colonnes fixées par docs/data_contract.md.
REQUIRED_COLUMNS = [
    "id",
    "name",
    "artists",
    "artist_ids",
    "release_date",
    "release_precision",
    "year",
    "genres",
    "selected_genres",
    "popularity",
    "duration_ms",
    "explicit",
    *AUDIO_FEATURES,
    "spotify_url",
]

LIST_COLUMNS = ["artists", "artist_ids", "genres", "selected_genres"]


class DataError(Exception):
    """Le fichier de données est absent ou ne respecte pas le contrat."""


@dataclass(frozen=True)
class DataSource:
    path: Path
    is_sample: bool


def find_source(root: Path = Path(".")) -> DataSource:
    """Choisit le fichier préparé s'il existe, sinon l'échantillon de démonstration."""
    processed = root / PROCESSED_PATH
    if processed.exists():
        return DataSource(processed, is_sample=False)
    sample = root / SAMPLE_PATH
    if sample.exists():
        return DataSource(sample, is_sample=True)
    raise DataError(
        f"Aucun fichier de données trouvé. Générez {PROCESSED_PATH} avec la commande "
        "de préparation décrite dans le README, puis relancez l'application."
    )


def validate(tracks: pd.DataFrame) -> None:
    """Vérifie les règles du contrat dont dépend l'interface."""
    missing = [column for column in REQUIRED_COLUMNS if column not in tracks.columns]
    if missing:
        raise DataError(
            "Le fichier de données ne respecte pas le contrat (docs/data_contract.md). "
            "Colonnes manquantes : " + ", ".join(missing)
        )
    if tracks["id"].duplicated().any():
        raise DataError(
            "Le fichier de données contient des identifiants en double : "
            "un titre doit apparaître une seule fois."
        )


def load_tracks(path: Path) -> pd.DataFrame:
    """Lit le fichier Parquet et renvoie une table conforme au contrat."""
    try:
        tracks = pd.read_parquet(path)
    except Exception as error:  # fichier illisible ou corrompu
        raise DataError(f"Impossible de lire {path} : {error}") from error
    validate(tracks)
    for column in LIST_COLUMNS:
        tracks[column] = tracks[column].map(lambda values: tuple(values) if values is not None else ())
    tracks["name"] = tracks["name"].fillna("")
    return tracks
