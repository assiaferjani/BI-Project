"""Valeurs réellement envoyées aux graphiques après les interactions."""

import json

import pytest

from tests.test_app import metric, run_app
from tests.ui_helpers import controlled_records, prepare_workspace


@pytest.fixture
def app(tmp_path, monkeypatch):
    prepare_workspace(tmp_path, records=controlled_records(60))
    return run_app(tmp_path, monkeypatch)


def trace(app, key):
    element = next(chart for chart in app.get("plotly_chart") if chart.proto.id.endswith(key))
    return json.loads(element.proto.spec)["data"][0]


def test_charts_start_with_the_controlled_annual_counts(app):
    assert not app.exception
    assert trace(app, "annual_chart")["y"] == [12] * 5
    assert trace(app, "annual_chart")["x"] == list(range(2020, 2025))
    assert trace(app, "growth_chart")["y"] == [0] * 4
    assert metric(app, "Variation en 2024") == "+0.00 %"


def test_filters_and_search_update_every_chart(app):
    app.slider(key="years").set_value((2020, 2023)).run()
    app.multiselect(key="categories").set_value(["cs.AI"]).run()
    app.text_input(key="query").set_value("TRANSFORMERS").run()
    assert not app.exception
    assert metric(app, "Articles uniques") == "6"
    assert trace(app, "annual_chart")["y"] == [3, 0, 0, 3]
    growth = trace(app, "growth_chart")
    assert growth["x"] == [2021]
    assert growth["y"] == [-100]
    assert metric(app, "Variation en 2023") == "Non calculable"
    categories = trace(app, "category_chart")
    assert dict(zip(categories["y"], categories["x"])) == {"cs.AI": 6, "cs.LG": 3}
    assert dict(zip(categories["y"], categories["customdata"])) == {"cs.AI": 100, "cs.LG": 50}


def test_single_year_does_not_compare_with_an_unselected_year(app):
    app.slider(key="years").set_value((2022, 2022)).run()
    assert not app.exception
    assert metric(app, "Variation en 2022") == "Non calculable"
    assert trace(app, "annual_chart")["y"] == [12]
    assert not any(chart.proto.id.endswith("growth_chart") for chart in app.get("plotly_chart"))
    assert any("Aucune variation" in item.value for item in app.info)


def test_empty_search_removes_charts_instead_of_showing_stale_values(app):
    app.text_input(key="query").set_value("introuvable-[.*").run()
    assert not app.exception
    assert metric(app, "Articles uniques") == "0"
    assert not app.get("plotly_chart")


def test_changing_filters_while_on_a_later_page_keeps_a_valid_page(app):
    app.number_input(key="page").set_value(3).run()
    app.multiselect(key="categories").set_value(["cs.CL"]).run()
    assert not app.exception
    assert metric(app, "Articles uniques") == "24"
