import io
from pathlib import Path

import pandas as pd

from ui.data import SAMPLE_PATH, load_tracks
from ui.export import export_table, file_name, to_csv_bytes
from ui.filters import Filters, apply_filters

REPO_ROOT = Path(__file__).resolve().parents[1]


def sample() -> pd.DataFrame:
    return load_tracks(REPO_ROOT / SAMPLE_PATH)


def read_back(data: bytes) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(data), dtype={"id": str}, keep_default_na=False)


def test_export_contains_exactly_the_filtered_tracks():
    filtered = apply_filters(sample(), Filters(1980, 1989, genres=("rock",)))
    exported = read_back(to_csv_bytes(filtered))
    assert len(filtered) > 0
    assert sorted(exported["id"]) == sorted(filtered["id"])
    assert exported["id"].is_unique
    assert exported["annee"].between(1980, 1989).all()
    assert exported["familles_de_genres"].str.contains("rock").all()


def test_export_flattens_lists_and_keeps_readable_columns():
    table = export_table(sample())
    assert list(table.columns[:6]) == [
        "id", "titre", "artistes", "annee", "date_sortie", "familles_de_genres",
    ]
    several = sample()[sample()["artists"].map(len) > 1].iloc[0]
    row = table[table["id"] == several["id"]].iloc[0]
    assert row["artistes"] == " ; ".join(several["artists"])
    assert set(table["explicite"]) <= {"oui", "non"}


def test_export_of_an_empty_result_keeps_the_header():
    filtered = apply_filters(sample(), Filters(1960, 2020, query="aucun titre ne contient ceci"))
    exported = read_back(to_csv_bytes(filtered))
    assert exported.empty
    assert "titre" in exported.columns


def test_export_opens_with_accents_in_a_spreadsheet():
    assert to_csv_bytes(sample()).startswith(b"\xef\xbb\xbf")


def test_file_name_recalls_the_filters():
    assert file_name(Filters(1960, 2020)) == "spotify_explorer_1960-2020.csv"
    name = file_name(Filters(1990, 1999, genres=("hip hop", "jazz"), query="Beyoncé / Jay-Z"))
    assert name == "spotify_explorer_1990-1999_hip-hop_jazz_beyonce-jay-z.csv"
