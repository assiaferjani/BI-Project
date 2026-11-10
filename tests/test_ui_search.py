import pandas as pd

from ui.filters import Filters, apply_filters
from ui.search import matches


def make_articles() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": ["a", "b", "c", "d"],
            "title": ["Attention Is All You Need?", "Graph networks (a survey)", "", "BERT for Français"],
            "abstract": ["We propose the Transformer.", "", "Large language models and C++.", "Pre-training."],
            "year": [2020, 2021, 2023, 2024],
            "selected_categories": [("cs.CL", "cs.LG"), ("cs.LG",), ("cs.CL",), ("cs.CL",)],
        }
    )


def found(query: str) -> list[str]:
    articles = make_articles()
    return articles[matches(articles, query)]["id"].tolist()


def test_search_ignores_case():
    assert found("TRANSFORMER") == ["a"]
    assert found("bert") == ["d"]


def test_search_looks_in_titles_and_abstracts():
    assert found("graph") == ["b"]
    assert found("language models") == ["c"]


def test_punctuation_is_literal_and_does_not_raise():
    assert found("need?") == ["a"]
    assert found("(a survey)") == ["b"]
    assert found("c++") == ["c"]
    assert found("[.*") == []
    assert found("\\") == []


def test_accents_and_capitals_do_not_break_the_search():
    assert found("FRANÇAIS") == ["d"]
    assert found("éèà ÿ") == []


def test_extra_spaces_are_ignored():
    assert found("  language   models ") == ["c"]


def test_empty_or_blank_search_keeps_everything():
    assert found("") == ["a", "b", "c", "d"]
    assert found("   ") == ["a", "b", "c", "d"]


def test_search_without_result_gives_an_empty_table():
    filtered = apply_filters(make_articles(), Filters(2020, 2024, query="introuvable"))
    assert filtered.empty
    assert filtered["id"].nunique() == 0


def test_search_combines_with_the_other_filters():
    filtered = apply_filters(make_articles(), Filters(2020, 2024, categories=("cs.CL",), query="r"))
    assert filtered["id"].tolist() == ["a", "c", "d"]
    filtered = apply_filters(make_articles(), Filters(2021, 2024, categories=("cs.CL",), query="r"))
    assert filtered["id"].tolist() == ["c", "d"]
