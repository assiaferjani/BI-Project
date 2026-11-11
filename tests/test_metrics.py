from pathlib import Path

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
import pytest

from src.metrics import (
    articles_per_category, category_share, submissions_per_year,
    unique_articles, yearly_change,
)
from src.prepare_data import prepare


@pytest.fixture
def articles():
    # A a deux catégories ; trois articles uniques et quatre appartenances.
    return pd.DataFrame({
        "id": ["a", "b", "c"],
        "year": [2020, 2020, 2021],
        "selected_categories": [["cs.AI", "cs.LG"], ["cs.AI"], ["cs.CL"]],
    })


def test_counts_and_shares_use_unique_articles(articles):
    duplicate = pd.concat([articles, articles.iloc[[0]]], ignore_index=True)
    assert unique_articles(duplicate) == 3
    counts = articles_per_category(duplicate)
    assert counts.to_dict("records") == [
        {"category": "cs.AI", "articles": 2},
        {"category": "cs.CL", "articles": 1},
        {"category": "cs.LG", "articles": 1},
    ]
    shares = category_share(duplicate)
    assert shares["share_pct"].tolist() == pytest.approx([200 / 3, 100 / 3, 100 / 3])
    assert shares["share_pct"].sum() == pytest.approx(400 / 3)
    assert submissions_per_year(duplicate).to_dict("records") == [
        {"year": 2020, "articles": 2}, {"year": 2021, "articles": 1},
    ]


@pytest.mark.parametrize("container", [list, tuple, np.array])
def test_category_containers_and_repeated_codes(articles, container):
    articles["selected_categories"] = articles["selected_categories"].map(
        lambda codes: container([*codes, codes[0]])
    )
    assert articles_per_category(articles)["articles"].tolist() == [2, 1, 1]


@pytest.mark.parametrize("function, columns", [
    (submissions_per_year, ["year", "articles"]),
    (articles_per_category, ["category", "articles"]),
    (category_share, ["category", "articles", "share_pct"]),
    (yearly_change, ["year", "articles", "change_pct"]),
])
def test_empty_results_keep_the_expected_columns(articles, function, columns):
    empty = articles.iloc[:0]
    result = function(empty)
    assert result.empty
    assert list(result.columns) == columns
    assert unique_articles(empty) == 0


def test_calendar_year_change_does_not_jump_over_missing_years():
    df = pd.DataFrame({"id": list("abcde"), "year": [2020, 2020, 2021, 2024, 2024]})
    result = yearly_change(df)
    assert result["year"].tolist() == [2020, 2021, 2024]
    assert pd.isna(result.loc[0, "change_pct"])
    assert result.loc[1, "change_pct"] == -50.0
    # 2023 est absent : ne pas comparer 2024 à 2021.
    assert pd.isna(result.loc[2, "change_pct"])


def test_known_period_zero_years_and_zero_denominator():
    df = pd.DataFrame({"id": ["a", "b"], "year": [2020, 2022]})
    result = yearly_change(df, year_range=(2020, 2023))
    assert result["year"].tolist() == [2020, 2021, 2022, 2023]
    assert result["articles"].tolist() == [1, 0, 1, 0]
    assert result.loc[1, "change_pct"] == -100.0
    assert pd.isna(result.loc[2, "change_pct"])
    assert result.loc[3, "change_pct"] == -100.0


def test_growth_example_is_twenty_percent():
    df = pd.DataFrame({"id": [f"id-{i}" for i in range(220)],
                       "year": [2020] * 100 + [2021] * 120})
    assert yearly_change(df).loc[1, "change_pct"] == 20.0


def test_single_year_and_empty_known_period(articles):
    only_2021 = articles[articles["year"] == 2021]
    assert yearly_change(only_2021)["change_pct"].isna().all()
    empty = yearly_change(articles.iloc[:0], year_range=(2020, 2024))
    assert empty["articles"].tolist() == [0] * 5
    assert empty["change_pct"].isna().all()


@pytest.mark.parametrize("period", [(2024, 2020), (0, 2024), (2020, 10000), (2021, 2024)])
def test_invalid_or_inconsistent_period_is_refused(articles, period):
    with pytest.raises(ValueError):
        submissions_per_year(articles, year_range=period)


def test_filtered_articles_are_the_only_denominator(articles):
    filtered = articles.iloc[[0, 2]]
    shares = category_share(filtered)
    assert unique_articles(filtered) == 2
    assert shares["share_pct"].tolist() == [50, 50, 50]


def test_functions_do_not_modify_shared_dataframe(articles):
    original = articles.copy(deep=True)
    for function in (unique_articles, submissions_per_year, articles_per_category,
                     category_share, yearly_change):
        function(articles)
    assert_frame_equal(articles, original)


def test_pipeline_to_parquet_to_metrics(tmp_path):
    source = Path(__file__).resolve().parents[1] / "data/sample/arxiv_demo.jsonl"
    output = tmp_path / "demo.parquet"
    prepare(source, output, source_version="synthetic-demo-v1")
    df = pd.read_parquet(output)
    assert unique_articles(df) == 3
    assert submissions_per_year(df)["year"].tolist() == [2020, 2021, 2024]
    assert articles_per_category(df)["articles"].tolist() == [2, 1, 1]
    assert yearly_change(df, year_range=(2020, 2024))["articles"].tolist() == [1, 1, 0, 0, 1]
