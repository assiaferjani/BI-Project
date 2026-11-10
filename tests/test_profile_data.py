from datetime import date
import json
from pathlib import Path
import subprocess
import sys

import pandas as pd
import pytest

from src.prepare_data import prepare
from src.profile_data import build_profile


@pytest.fixture
def frame(tmp_path):
    source = Path(__file__).resolve().parents[1] / "data/sample/arxiv_demo.jsonl"
    target = tmp_path / "demo.parquet"
    prepare(source, target)
    return pd.read_parquet(target)


def test_profile_on_known_demo(frame):
    result = build_profile(frame)
    assert result["rows"] == result["unique_articles"] == 3
    assert all(result["checks"].values())
    assert result["missing_text"] == {"title": 0, "abstract": 1, "authors": 0}
    assert result["articles_with_multiple_selected_categories"] == 1
    assert result["category_memberships"] == 4
    assert result["first_submission"] == "2020-01-01"
    assert result["last_submission"] == "2024-12-31"
    assert result["annual"][-1]["change_pct"] is None
    # Aucun NaN non standard et aucun texte d'article dans ce bilan.
    text = json.dumps(result, allow_nan=False)
    assert "Résumé fictif" not in text


@pytest.mark.parametrize("field,value,reason", [
    ("id", "", "ids_nonempty_strings"),
    ("year", 2023, "year_matches_submission"),
    ("submitted_at", date(2023, 1, 1), "year_matches_submission"),
    ("selected_categories", "cs.AI", "selected_categories_valid"),
    ("selected_categories", ["math.AG"], "selected_categories_in_original"),
    ("categories", ["cs.AI", "cs.AI"], "categories_valid"),
    ("title", None, "text_fields_are_strings"),
])
def test_invalid_contract_is_refused(frame, field, value, reason):
    frame.at[0, field] = value
    with pytest.raises(ValueError, match=reason):
        build_profile(frame)


def test_duplicates_are_rejected_instead_of_hidden(frame):
    with pytest.raises(ValueError, match="ids_unique"):
        build_profile(pd.concat([frame, frame.iloc[[0]]], ignore_index=True))


def test_missing_column_is_named(frame):
    with pytest.raises(ValueError, match="authors"):
        build_profile(frame.drop(columns="authors"))


def test_empty_parquet_is_reported_without_fabricated_dates(frame):
    result = build_profile(frame.iloc[:0])
    assert result["unique_articles"] == 0
    assert result["first_submission"] is None
    assert result["annual"] == result["categories"] == []


def test_profile_command(tmp_path, frame):
    source = tmp_path / "demo.parquet"
    frame.to_parquet(source, index=False)
    dest = tmp_path / "report.json"
    result = subprocess.run(
        [sys.executable, "-m", "src.profile_data", "--input", str(source),
         "--output", str(dest)], capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(dest.read_text())["unique_articles"] == 3
