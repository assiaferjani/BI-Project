"""Tests de bout en bout de l'interface, sur des données fictives contrôlées."""

import pytest
from streamlit.testing.v1 import AppTest

from tests.ui_helpers import REPO_ROOT, controlled_records, prepare_workspace


def run_app(root, monkeypatch) -> AppTest:
    monkeypatch.chdir(root)
    return AppTest.from_file(str(REPO_ROOT / "app.py"), default_timeout=30).run()


@pytest.fixture
def app(tmp_path, monkeypatch):
    """Application lancée sur 60 articles : 12 par année, catégories en cycle de 5."""
    prepare_workspace(tmp_path, records=controlled_records(60))
    return run_app(tmp_path, monkeypatch)


def metric(app: AppTest, label: str) -> str:
    return next(m.value for m in app.metric if m.label == label)


def test_app_starts_on_the_project_demo_and_says_it_is_fictitious(tmp_path, monkeypatch):
    prepare_workspace(tmp_path)
    app = run_app(tmp_path, monkeypatch)
    assert not app.exception
    assert any("Données fictives" in warning.value for warning in app.warning)
    assert metric(app, "Articles uniques") == "3"
    assert metric(app, "Catégories étudiées") == "3"


def test_missing_data_shows_an_instruction_instead_of_an_error(tmp_path, monkeypatch):
    app = run_app(tmp_path, monkeypatch)
    assert not app.exception
    assert any("README" in error.value for error in app.error)


def test_category_filter_counts_unique_articles(app):
    # cs.AI : positions 0 et 3 du cycle de 5, soit 24 articles sur 60.
    app.multiselect(key="categories").set_value(["cs.AI"]).run()
    assert not app.exception
    assert metric(app, "Articles uniques") == "24"


def test_two_categories_do_not_count_an_article_twice(app):
    # cs.AI ou cs.LG : positions 0, 1 et 3 ; « cs.AI cs.LG » compte une fois.
    app.multiselect(key="categories").set_value(["cs.AI", "cs.LG"]).run()
    assert metric(app, "Articles uniques") == "36"


def test_year_filter_changes_the_total(app):
    app.slider(key="years").set_value((2021, 2022)).run()
    assert not app.exception
    assert metric(app, "Articles uniques") == "24"
    assert metric(app, "Période filtrée") == "2021 à 2022"


def test_search_filters_the_total_and_ignores_case(app):
    # Un article sur quatre a « Transformers » dans son titre.
    app.text_input(key="query").set_value("tRANSFORMERS").run()
    assert not app.exception
    assert metric(app, "Articles uniques") == "15"


def test_search_without_result_shows_a_message_and_no_error(app):
    app.text_input(key="query").set_value("zzz (introuvable) [?").run()
    assert not app.exception
    assert metric(app, "Articles uniques") == "0"
    assert any("Aucun article ne correspond" in warning.value for warning in app.warning)
    assert len(app.dataframe) == 0


def test_article_detail_handles_a_missing_abstract(app):
    app.text_input(key="query").set_value("Article 007").run()
    app.selectbox(key="detail").set_value("test-007").run()
    assert not app.exception
    assert any(header.value.startswith("Article 007") for header in app.subheader)
    assert any("Résumé non disponible" in text.value for text in app.markdown)


def test_second_page_lists_the_next_articles(app):
    app.number_input(key="page").set_value(2).run()
    assert not app.exception
    assert any("Articles 26 à 50" in text.value for text in app.markdown)
