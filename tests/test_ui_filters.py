import pandas as pd

from ui.filters import Filters, apply_filters, available_genres, year_bounds


def make_tracks() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": ["a", "b", "c", "d"],
            "year": [1960, 1985, 2020, 2021],
            "selected_genres": [("pop", "rock"), ("pop",), ("jazz",), ("rock",)],
        }
    )


def ids(tracks: pd.DataFrame) -> list[str]:
    return tracks["id"].tolist()


def test_year_bounds_are_included():
    filtered = apply_filters(make_tracks(), Filters(1960, 2020))
    assert ids(filtered) == ["a", "b", "c"]


def test_years_outside_the_range_are_excluded():
    filtered = apply_filters(make_tracks(), Filters(1961, 2019))
    assert ids(filtered) == ["b"]


def test_no_genre_selected_means_all_genres():
    filtered = apply_filters(make_tracks(), Filters(1960, 2021, genres=()))
    assert ids(filtered) == ["a", "b", "c", "d"]


def test_several_genres_keep_tracks_matching_at_least_one():
    filtered = apply_filters(make_tracks(), Filters(1960, 2021, genres=("rock", "jazz")))
    assert ids(filtered) == ["a", "c", "d"]


def test_track_in_two_selected_genres_appears_once():
    filtered = apply_filters(make_tracks(), Filters(1960, 2021, genres=("pop", "rock")))
    assert ids(filtered) == ["a", "b", "d"]
    assert filtered["id"].is_unique


def test_filters_without_match_return_an_empty_table():
    filtered = apply_filters(make_tracks(), Filters(1990, 2000, genres=("jazz",)))
    assert filtered.empty
    assert list(filtered.columns) == ["id", "year", "selected_genres"]


def test_available_genres_are_sorted_and_unique():
    assert available_genres(make_tracks()) == ["jazz", "pop", "rock"]


def test_year_bounds():
    assert year_bounds(make_tracks()) == (1960, 2021)
