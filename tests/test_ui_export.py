import io

import pandas as pd
import pytest

from tests.ui_helpers import controlled_records, prepare_workspace
from ui.data import load_articles
from ui.export import export_table, file_name, to_csv_bytes
from ui.filters import Filters, apply_filters


@pytest.fixture
def articles(tmp_path) -> pd.DataFrame:
    return load_articles(prepare_workspace(tmp_path, records=controlled_records(60)))


def read_back(data: bytes) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(data), dtype={"id": str}, keep_default_na=False)


def test_export_contains_exactly_the_filtered_articles(articles):
    filtered = apply_filters(articles, Filters(2021, 2022, categories=("cs.LG",)))
    exported = read_back(to_csv_bytes(filtered))
    assert len(filtered) > 0
    assert sorted(exported["id"]) == sorted(filtered["id"])
    assert exported["id"].is_unique
    assert exported["annee"].between(2021, 2022).all()
    assert exported["categories_etudiees"].str.contains("cs.LG", regex=False).all()


def test_export_has_readable_columns_and_flat_lists(articles):
    table = export_table(articles)
    assert list(table.columns) == [
        "id", "titre", "auteurs", "date_premier_depot", "annee",
        "categories_etudiees", "toutes_les_categories", "resume", "lien_arxiv",
    ]
    row = table[table["id"] == "test-003"].iloc[0]
    assert row["categories_etudiees"] == "cs.AI ; cs.LG"
    # stat.ML est hors périmètre : gardée dans toutes les catégories seulement.
    row = table[table["id"] == "test-004"].iloc[0]
    assert (row["categories_etudiees"], row["toutes_les_categories"]) == ("cs.CL", "cs.CL ; stat.ML")


def test_export_of_an_empty_result_keeps_the_header(articles):
    filtered = apply_filters(articles, Filters(2020, 2024, query="aucun article ne contient ceci"))
    exported = read_back(to_csv_bytes(filtered))
    assert exported.empty
    assert "titre" in exported.columns


def test_export_opens_with_accents_in_a_spreadsheet(articles):
    assert to_csv_bytes(articles).startswith(b"\xef\xbb\xbf")


def test_file_name_recalls_the_filters():
    assert file_name(Filters(2020, 2024)) == "arxiv_explorer_2020-2024.csv"
    name = file_name(Filters(2021, 2023, categories=("cs.AI", "cs.CL"), query="Large  Language/Models?"))
    assert name == "arxiv_explorer_2021-2023_cs.AI_cs.CL_large-language-models.csv"
