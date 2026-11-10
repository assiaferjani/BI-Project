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
