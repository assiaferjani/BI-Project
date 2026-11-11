import pandas as pd
import pytest

from tests.ui_helpers import prepare_workspace
from ui.data import (
    DEMO_PATH,
    PROCESSED_PATH,
    REQUIRED_COLUMNS,
    DataError,
    find_source,
    load_articles,
    validate,
)


def test_pipeline_output_respects_the_contract_expected_by_the_interface(tmp_path):
    articles = load_articles(prepare_workspace(tmp_path))
    assert list(articles.columns) == REQUIRED_COLUMNS
    assert articles["id"].tolist() == ["demo-001", "demo-002", "demo-003"]
    assert articles["selected_categories"].tolist() == [("cs.AI", "cs.LG"), ("cs.CL",), ("cs.AI",)]
    # Résumé absent dans la source : chaîne vide, jamais de valeur manquante.
    assert articles.loc[articles["id"] == "demo-003", "abstract"].item() == ""
    assert not articles[["title", "abstract", "authors"]].isna().any().any()


def test_processed_file_is_preferred_to_the_demo(tmp_path):
    for relative in (PROCESSED_PATH, DEMO_PATH):
        (tmp_path / relative).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / relative).touch()
    source = find_source(tmp_path)
    assert source.path == tmp_path / PROCESSED_PATH
    assert not source.is_demo


def test_demo_is_used_when_processed_file_is_missing(tmp_path):
    (tmp_path / DEMO_PATH).parent.mkdir(parents=True)
    (tmp_path / DEMO_PATH).touch()
    assert find_source(tmp_path).is_demo


def test_missing_data_gives_a_useful_instruction(tmp_path):
    with pytest.raises(DataError, match="README"):
        find_source(tmp_path)


def test_missing_column_is_named_in_the_error():
    articles = pd.DataFrame(columns=[c for c in REQUIRED_COLUMNS if c != "year"])
    with pytest.raises(DataError, match="year"):
        validate(articles)


def test_duplicated_id_is_refused():
    articles = pd.DataFrame({column: ["x", "x"] for column in REQUIRED_COLUMNS})
    with pytest.raises(DataError, match="double"):
        validate(articles)


def test_unreadable_file_is_reported(tmp_path):
    broken = tmp_path / "articles.parquet"
    broken.write_text("pas un fichier parquet")
    with pytest.raises(DataError, match="Impossible de lire"):
        load_articles(broken)
