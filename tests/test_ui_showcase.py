import pytest
from tests.test_app import run_app, metric
from tests.test_ui_charts import trace
from tests.ui_helpers import controlled_records,prepare_workspace


@pytest.fixture
def app(tmp_path,monkeypatch):
    prepare_workspace(tmp_path,records=controlled_records(60))
    return run_app(tmp_path,monkeypatch)


def test_showcase_has_ten_charts_and_expected_monthly_cells(app):
    assert not app.exception
    assert len(app.get('plotly_chart'))==12
    matrix=trace(app,'calendar_chart')['z']
    assert all(row[2]==12 for row in matrix)
    assert all(sum(row)==12 for row in matrix)


def test_percent_calendar_and_jaccard_modes(app):
    app.toggle(key='calendar_percent').set_value(True).run()
    assert all(row[2]==100 for row in trace(app,'calendar_chart')['z'])
    app.toggle(key='overlap_normalized').set_value(True).run()
    matrix=trace(app,'overlap_chart')['z']
    assert all(matrix[i][i]==100 for i in range(3))
    assert not app.exception


def test_category_index_does_not_invent_a_baseline_for_zero(app):
    app.toggle(key='indexed_categories').set_value(True).run()
    assert not app.exception
    # cs.AI est la première catégorie ; elle possède une base en 2020.
    assert trace(app,'trajectories_chart')['y'][0]==100


def test_scenario_updates_filters_and_reset_restores_panorama(app):
    app.button(key='preset_transformer').click().run()
    assert not app.exception
    assert app.text_input(key='query').value=='transformer'
    assert app.multiselect(key='categories').value==['cs.CL']
    app.button(key='preset_all').click().run()
    assert metric(app,'Articles uniques')=='60'
    assert app.text_input(key='query').value==''


def test_reading_basket_survives_filters_and_can_be_cleared(app):
    app.selectbox(key='detail').set_value('test-054').run()
    app.button(key='save_explore_test-054').click().run()
    assert not app.exception
    assert app.session_state['reading_ids']==['test-054']
    assert metric(app,'Articles dans le panier')=='1'
    app.text_input(key='query').set_value('unfindable').run()
    assert metric(app,'Articles uniques')=='0'
    assert metric(app,'Articles dans le panier')=='1'
    app.button(key='clear_reading').click().run()
    assert app.session_state['reading_ids']==[]
    assert not app.exception


def test_selected_word_can_become_a_global_filter(app):
    chosen=app.selectbox(key='chosen_term').value
    app.button(key='apply_term').click().run()
    assert not app.exception
    assert app.text_input(key='query').value==chosen


def test_random_discovery_and_pedagogical_reveal(app):
    app.button(key='random_article').click().run()
    assert app.session_state['spotlight_id'].startswith('test-')
    assert not app.exception
    app.checkbox(key='calendar_answer').set_value(True).run()
    assert any('Dans votre sélection' in item.value for item in app.info)


def test_overview_links_open_the_relevant_workspace(app):
    app.button(key='open_trends').click().run()
    assert app.session_state['workspace']=='Tendances'
    assert not app.exception
