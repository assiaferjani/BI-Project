"""Tests de bout en bout de l'interface, sur l'échantillon de démonstration."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from ui.data import PROCESSED_PATH, SAMPLE_PATH, load_tracks

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def app(monkeypatch):
    if (REPO_ROOT / PROCESSED_PATH).exists():
        pytest.skip("le fichier préparé est présent : ces tests visent l'échantillon")
    monkeypatch.chdir(REPO_ROOT)
    return AppTest.from_file(str(REPO_ROOT / "app.py"), default_timeout=30).run()


def metric(app: AppTest, label: str) -> str:
    return next(m.value for m in app.metric if m.label == label)


def test_app_starts_on_the_sample_and_says_so(app):
    assert not app.exception
    assert any("Données de démonstration" in warning.value for warning in app.warning)
    sample = load_tracks(REPO_ROOT / SAMPLE_PATH)
    assert metric(app, "Titres uniques") == str(sample["id"].nunique())


def test_genre_filter_changes_the_total(app):
    sample = load_tracks(REPO_ROOT / SAMPLE_PATH)
    expected = sample["selected_genres"].map(lambda genres: "jazz" in genres).sum()
    app.multiselect(key="genres").set_value(["jazz"]).run()
    assert not app.exception
    assert metric(app, "Titres uniques") == str(expected)


def test_year_filter_changes_the_total(app):
    sample = load_tracks(REPO_ROOT / SAMPLE_PATH)
    expected = sample["year"].between(1990, 1999).sum()
    app.slider(key="years").set_value((1990, 1999)).run()
    assert not app.exception
    assert metric(app, "Titres uniques") == str(expected)
    assert metric(app, "Période filtrée") == "1990 à 1999"


def test_search_filters_the_total_and_ignores_accents(app):
    sample = load_tracks(REPO_ROOT / SAMPLE_PATH)
    expected = sample["search_text"].str.contains("love", regex=False).sum()
    assert expected > 0
    app.text_input(key="query").set_value("LÖVE").run()
    assert not app.exception
    assert metric(app, "Titres uniques") == str(expected)


def test_search_without_result_shows_a_message_and_no_error(app):
    app.text_input(key="query").set_value("zzz (introuvable) [?").run()
    assert not app.exception
    assert metric(app, "Titres uniques") == "0"
    assert any("Aucun titre ne correspond" in warning.value for warning in app.warning)
    assert len(app.dataframe) == 0


def test_track_detail_opens_from_the_list(app):
    sample = load_tracks(REPO_ROOT / SAMPLE_PATH)
    top = sample.sort_values(["popularity", "id"], ascending=[False, True]).iloc[0]
    app.selectbox(key="detail").set_value(top["id"]).run()
    assert not app.exception
    assert any(header.value == (top["name"] or "(sans titre)") for header in app.subheader)


def test_second_page_lists_the_next_tracks(app):
    app.number_input(key="page").set_value(2).run()
    assert not app.exception
    assert any("Titres 26 à 50" in text.value for text in app.markdown)
