import pandas as pd

from ui.filters import Filters, apply_filters, available_categories, year_bounds


def make_articles() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": ["a", "b", "c", "d"],
            "year": [2020, 2022, 2024, 2025],
            "selected_categories": [("cs.AI", "cs.LG"), ("cs.AI",), ("cs.CL",), ("cs.LG",)],
        }
    )


def ids(articles: pd.DataFrame) -> list[str]:
    return articles["id"].tolist()


def test_year_bounds_are_included():
    filtered = apply_filters(make_articles(), Filters(2020, 2024))
    assert ids(filtered) == ["a", "b", "c"]


def test_years_outside_the_range_are_excluded():
    filtered = apply_filters(make_articles(), Filters(2021, 2023))
    assert ids(filtered) == ["b"]


def test_no_category_selected_means_all_categories():
    filtered = apply_filters(make_articles(), Filters(2020, 2025, categories=()))
    assert ids(filtered) == ["a", "b", "c", "d"]


def test_several_categories_keep_articles_matching_at_least_one():
    filtered = apply_filters(make_articles(), Filters(2020, 2025, categories=("cs.LG", "cs.CL")))
    assert ids(filtered) == ["a", "c", "d"]


def test_article_in_two_selected_categories_appears_once():
    filtered = apply_filters(make_articles(), Filters(2020, 2025, categories=("cs.AI", "cs.LG")))
    assert ids(filtered) == ["a", "b", "d"]
    assert filtered["id"].is_unique


def test_filters_without_match_return_an_empty_table():
    filtered = apply_filters(make_articles(), Filters(2021, 2021, categories=("cs.CL",)))
    assert filtered.empty
    assert list(filtered.columns) == ["id", "year", "selected_categories"]


def test_available_categories_are_sorted_and_unique():
    assert available_categories(make_articles()) == ["cs.AI", "cs.CL", "cs.LG"]


def test_year_bounds():
    assert year_bounds(make_articles()) == (2020, 2025)
