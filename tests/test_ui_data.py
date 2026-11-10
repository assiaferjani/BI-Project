from pathlib import Path

import pandas as pd
import pytest

from ui.data import (
    PROCESSED_PATH,
    REQUIRED_COLUMNS,
    SAMPLE_PATH,
    DataError,
    find_source,
    load_tracks,
    validate,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_sample_respects_the_data_contract():
    tracks = load_tracks(REPO_ROOT / SAMPLE_PATH)
    assert set(REQUIRED_COLUMNS) <= set(tracks.columns)
    assert tracks["id"].is_unique
    assert tracks["selected_genres"].map(len).min() >= 1
    assert tracks["year"].between(1960, 2020).all()
    assert (tracks["spotify_url"] == "https://open.spotify.com/track/" + tracks["id"]).all()


def test_processed_file_is_preferred_to_the_sample(tmp_path):
    for relative in (PROCESSED_PATH, SAMPLE_PATH):
        (tmp_path / relative).parent.mkdir(parents=True)
        (tmp_path / relative).touch()
    source = find_source(tmp_path)
    assert source.path == tmp_path / PROCESSED_PATH
    assert not source.is_sample


def test_sample_is_used_when_processed_file_is_missing(tmp_path):
    (tmp_path / SAMPLE_PATH).parent.mkdir(parents=True)
    (tmp_path / SAMPLE_PATH).touch()
    assert find_source(tmp_path).is_sample


def test_missing_data_gives_a_useful_instruction(tmp_path):
    with pytest.raises(DataError, match="README"):
        find_source(tmp_path)


def test_missing_column_is_named_in_the_error():
    tracks = pd.DataFrame(columns=[c for c in REQUIRED_COLUMNS if c != "year"])
    with pytest.raises(DataError, match="year"):
        validate(tracks)


def test_duplicated_id_is_refused():
    tracks = pd.DataFrame({column: ["x", "x"] for column in REQUIRED_COLUMNS})
    with pytest.raises(DataError, match="double"):
        validate(tracks)
