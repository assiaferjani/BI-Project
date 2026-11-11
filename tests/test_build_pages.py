import zipfile

import pandas as pd

from scripts.build_pages import ONLINE_DATA, build_site, slim, streamlit_config
from tests.ui_helpers import controlled_records, prepare_workspace
from ui.data import REQUIRED_COLUMNS, has_abstracts, load_articles


def test_slim_keeps_every_article_and_only_empties_the_abstracts(tmp_path):
    source = prepare_workspace(tmp_path, records=controlled_records())
    output = tmp_path / "online.parquet"
    assert slim(source, output) == 60

    full, online = load_articles(source), load_articles(output)
    assert list(online.columns) == REQUIRED_COLUMNS
    assert has_abstracts(full) and not has_abstracts(online)
    pd.testing.assert_frame_equal(online.drop(columns="abstract"), full.drop(columns="abstract"))


def test_site_contains_the_page_the_application_and_the_data(tmp_path):
    data = tmp_path / "online.parquet"
    slim(prepare_workspace(tmp_path, records=controlled_records()), data)
    site = tmp_path / "_site"
    build_site(site, data=data)

    page = (site / "index.html").read_text(encoding="utf-8")
    assert "__STREAMLIT_CONFIG__" not in page
    assert '"theme.primaryColor": "#087f78"' in page
    assert (site / ".nojekyll").exists()
    assert (site / "data" / "articles.parquet").read_bytes() == data.read_bytes()
    with zipfile.ZipFile(site / "app.zip") as archive:
        names = set(archive.namelist())
    # La feuille de style est lue par ui/design.py au démarrage.
    assert {"app.py", "ui/data.py", "ui/theme.css", "src/metrics.py"} <= names
    assert not any("__pycache__" in name for name in names)


def test_streamlit_options_are_flattened_for_stlite():
    assert streamlit_config()["theme.base"] == "light"


def test_published_data_matches_the_documented_article_count():
    # Le fichier versionné doit rester celui du bilan (docs/data_findings.md).
    online = pd.read_parquet(ONLINE_DATA, columns=["id", "abstract"])
    assert online["id"].nunique() == len(online) == 229_620
    assert online["abstract"].eq("").all()
