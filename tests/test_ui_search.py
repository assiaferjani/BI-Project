import pandas as pd

from ui.filters import Filters, apply_filters
from ui.search import add_search_column, matches, normalize


def make_tracks() -> pd.DataFrame:
    tracks = pd.DataFrame(
        {
            "id": ["a", "b", "c", "d"],
            "name": ["Élan Vital", "What's Up? (Live)", "", "Blue in Green"],
            "artists": [("Zoé",), ("4 Non Blondes",), ("Beyoncé", "JAY-Z"), ("Miles Davis",)],
            "year": [1990, 1993, 2003, 1960],
            "selected_genres": [("pop",), ("rock",), ("pop", "hip hop"), ("jazz",)],
        }
    )
    return add_search_column(tracks)


def found(query: str) -> list[str]:
    tracks = make_tracks()
    return tracks[matches(tracks, query)]["id"].tolist()


def test_normalize_ignores_case_accents_and_extra_spaces():
    assert normalize("  ÉLAN   vital ") == "elan vital"


def test_search_ignores_case_and_accents():
    assert found("elan VITAL") == ["a"]
    assert found("beyonce") == ["c"]


def test_search_looks_in_titles_and_artists():
    assert found("blue") == ["d"]
    assert found("miles") == ["d"]


def test_punctuation_is_literal_and_does_not_raise():
    assert found("what's up? (") == ["b"]
    assert found("[.*") == []
    assert found("\\") == []


def test_empty_or_blank_search_keeps_everything():
    assert found("") == ["a", "b", "c", "d"]
    assert found("   ") == ["a", "b", "c", "d"]


def test_search_without_result_gives_an_empty_table():
    filtered = apply_filters(make_tracks(), Filters(1960, 2020, query="introuvable"))
    assert filtered.empty
    assert filtered["id"].nunique() == 0


def test_search_combines_with_the_other_filters():
    filtered = apply_filters(make_tracks(), Filters(1960, 2020, genres=("pop",), query="z"))
    assert filtered["id"].tolist() == ["a", "c"]
    filtered = apply_filters(make_tracks(), Filters(1995, 2020, genres=("pop",), query="z"))
    assert filtered["id"].tolist() == ["c"]
