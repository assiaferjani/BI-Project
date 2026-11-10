from copy import deepcopy
from datetime import date
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pyarrow.parquet as pq
import pytest

from src.prepare_data import SCHEMA, prepare


def article(identifier="2001.00001", created="Wed, 1 Jan 2020 00:00:00 GMT", **changes):
    return {"id": identifier, "title": " Une  étude\n BI ", "abstract": "Résumé",
            "authors": "A", "categories": "cs.AI cs.LG",
            "versions": [{"version": "v1", "created": created}], **changes}


def run(tmp_path, records, **kwargs):
    source = tmp_path / "source.jsonl"
    source.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
    output = tmp_path / "articles.parquet"
    report = prepare(source, output, **kwargs)
    return pq.read_table(output), report


def test_first_version_not_update_date_and_exact_identifier(tmp_path):
    record = article("0001.00100", update_date="2024-06-01")
    record["versions"].insert(0, {"version": "v2", "created": "Mon, 1 Jan 2024 12:00:00 GMT"})
    table, report = run(tmp_path, [record])
    row = table.to_pylist()[0]
    assert row["id"] == "0001.00100"
    assert row["submitted_at"] == date(2020, 1, 1)
    assert row["year"] == 2020
    assert row["title"] == "Une étude BI"
    assert row["arxiv_url"] == "https://arxiv.org/abs/0001.00100"
    assert report["outcomes"]["retained"] == 1


def test_category_overlap_duplicates_and_batch_boundaries(tmp_path):
    first = article(categories="cs.AI cs.LG cs.AI math.ST")
    duplicate = deepcopy(first)
    duplicate["title"] = "ne doit pas remplacer la première occurrence"
    records = [first, article("second", categories="cs.CL"), duplicate,
               article("third", categories="cs.AI")]
    table, report = run(tmp_path, records, batch_size=1)
    rows = table.to_pylist()
    assert table.num_rows == 3
    assert rows[0]["title"] == "Une étude BI"
    assert rows[0]["categories"] == ["cs.AI", "cs.LG", "math.ST"]
    assert rows[0]["selected_categories"] == ["cs.AI", "cs.LG"]
    assert sum(len(r["selected_categories"]) for r in rows) == 4
    assert report["outcomes"]["duplicate_retained_id"] == 1


def test_inclusive_year_boundaries(tmp_path):
    records = [article(str(i), created=d) for i, d in enumerate([
        "Tue, 31 Dec 2019 23:59:59 GMT", "Wed, 1 Jan 2020 00:00:00 GMT",
        "Tue, 31 Dec 2024 23:59:59 GMT", "Wed, 1 Jan 2025 00:00:00 GMT",
    ])]
    table, report = run(tmp_path, records)
    assert table.column("id").to_pylist() == ["1", "2"]
    assert report["outcomes"]["outside_years"] == 2


@pytest.mark.parametrize("record, reason", [
    ([], "invalid_record"),
    (article(id=123), "invalid_id"),
    (article(id=""), "invalid_id"),
    (article(versions=None), "missing_v1"),
    (article(versions=[{"version": "v2"}]), "missing_v1"),
    (article(created="not a date"), "invalid_v1_date"),
    (article(created=None), "invalid_v1_date"),
    (article(categories=None), "invalid_categories"),
    (article(categories="math.AG"), "outside_categories"),
])
def test_invalid_records_have_a_counted_reason(tmp_path, record, reason):
    table, report = run(tmp_path, [record])
    assert table.num_rows == 0
    assert table.schema == SCHEMA
    assert report["outcomes"][reason] == 1
    assert sum(report["outcomes"].values()) == report["lines_read"] == 1


def test_missing_text_is_kept_and_reported(tmp_path):
    table, report = run(tmp_path, [article(title=None, abstract="", authors=17)])
    assert table.to_pylist()[0]["title"] == ""
    assert report["missing_text_in_retained"] == {"title": 1, "abstract": 1, "authors": 1}


def test_invalid_json_blank_lines_hash_and_saved_report(tmp_path):
    source = tmp_path / "source.jsonl"
    raw = b'\n{broken}\n\xff\n' + json.dumps(article()).encode() + b'\n'
    source.write_bytes(raw)
    output = tmp_path / "result.parquet"
    report = prepare(source, output, source_version="test-v1")
    assert report["lines_read"] == sum(report["outcomes"].values()) == 4
    assert report["outcomes"]["blank_lines"] == 1
    assert report["outcomes"]["invalid_json"] == 2
    assert report["source"]["sha256"] == hashlib.sha256(raw).hexdigest()
    assert report["source"]["version"] == "test-v1"
    assert json.loads(output.with_suffix(".quality.json").read_text()) == report


def test_empty_input_produces_a_readable_typed_parquet(tmp_path):
    source = tmp_path / "empty.jsonl"
    source.touch()
    output = tmp_path / "empty.parquet"
    report = prepare(source, output)
    assert report["lines_read"] == 0
    assert pq.read_table(output).schema == SCHEMA
    assert pq.read_table(output).num_rows == 0


@pytest.mark.parametrize("options", [
    {"start_year": 2025, "end_year": 2020}, {"batch_size": 0}, {"categories": []},
])
def test_invalid_parameters_do_not_write_outputs(tmp_path, options):
    output = tmp_path / "result.parquet"
    with pytest.raises(ValueError):
        prepare(tmp_path / "missing.jsonl", output, **options)
    assert not output.exists()


def test_input_cannot_be_overwritten(tmp_path):
    source = tmp_path / "source.parquet"
    source.write_text("do not modify")
    with pytest.raises(ValueError, match="source"):
        prepare(source, source)
    assert source.read_text() == "do not modify"


def test_cli_demo(tmp_path):
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "demo.parquet"
    result = subprocess.run([
        sys.executable, "-m", "src.prepare_data", "--input",
        str(root / "data/sample/arxiv_demo.jsonl"), "--output", str(output),
        "--source-version", "synthetic-demo-v1",
    ], cwd=root, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    report = json.loads(output.with_suffix(".quality.json").read_text())
    assert report["lines_read"] == 6
    assert report["outcomes"]["retained"] == 3
    assert report["outcomes"]["duplicate_retained_id"] == 1
    assert report["outcomes"]["outside_years"] == 1
    assert report["outcomes"]["outside_categories"] == 1
