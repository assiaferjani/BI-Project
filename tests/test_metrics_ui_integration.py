"""Vérifie le contrat entre pipeline, interface, indicateurs et export."""

import io

import pandas as pd

from src.metrics import category_share, unique_articles, yearly_change
from tests.ui_helpers import controlled_records, prepare_workspace
from ui.data import load_articles
from ui.export import to_csv_bytes
from ui.filters import Filters, apply_filters


def test_filtered_metrics_and_export_describe_the_same_articles(tmp_path):
    articles = load_articles(prepare_workspace(tmp_path, records=controlled_records(60)))
    filtered = apply_filters(articles, Filters(2020, 2023, ("cs.AI",), "TRANSFORMERS"))

    # Identifiants déterminés à la main à partir des 60 lignes contrôlées.
    expected_ids = {"test-000", "test-008", "test-020", "test-028", "test-040", "test-048"}
    assert set(filtered["id"]) == expected_ids
    assert unique_articles(filtered) == 6
    annual = yearly_change(filtered, year_range=(2020, 2023))
    assert annual["articles"].tolist() == [3, 0, 0, 3]
    assert annual.loc[1, "change_pct"] == -100
    assert pd.isna(annual.loc[3, "change_pct"])
    shares = category_share(filtered).set_index("category")
    assert shares["articles"].to_dict() == {"cs.AI": 6, "cs.LG": 3}
    assert shares["share_pct"].to_dict() == {"cs.AI": 100, "cs.LG": 50}
    exported = pd.read_csv(io.BytesIO(to_csv_bytes(filtered)), dtype={"id": str})
    assert set(exported["id"]) == expected_ids
    assert len(exported) == unique_articles(filtered)


def test_empty_search_agrees_across_metrics_and_export(tmp_path):
    articles = load_articles(prepare_workspace(tmp_path, records=controlled_records(60)))
    filtered = apply_filters(articles, Filters(2020, 2024, query="[aucun article]"))
    assert unique_articles(filtered) == 0
    assert yearly_change(filtered, year_range=(2020, 2024))["articles"].tolist() == [0] * 5
    assert category_share(filtered).empty
    assert pd.read_csv(io.BytesIO(to_csv_bytes(filtered))).empty
