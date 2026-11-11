"""Prépare un sous-ensemble arXiv sans charger le snapshot entier en mémoire."""

import argparse
from collections import Counter
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import json
from pathlib import Path
import platform
import tempfile
from urllib.parse import quote

import pyarrow as pa
import pyarrow.parquet as pq


SCHEMA = pa.schema([
    ("id", pa.string()),
    ("title", pa.string()),
    ("abstract", pa.string()),
    ("authors", pa.string()),
    ("submitted_at", pa.date32()),
    ("year", pa.int16()),
    ("categories", pa.list_(pa.string())),
    ("selected_categories", pa.list_(pa.string())),
    ("arxiv_url", pa.string()),
])
REASONS = (
    "blank_lines", "invalid_json", "invalid_record", "invalid_id",
    "missing_v1", "invalid_v1_date", "outside_years", "invalid_categories",
    "outside_categories", "duplicate_retained_id", "retained",
)


def clean_text(value):
    """Un champ textuel absent ou mal typé devient une chaîne vide."""
    return " ".join(value.split()) if isinstance(value, str) else ""


def normalize(record, start_year, end_year, allowed_categories):
    """Retourne (article, None), ou (None, motif unique d'exclusion)."""
    if not isinstance(record, dict):
        return None, "invalid_record"
    identifier = record.get("id")
    if not isinstance(identifier, str) or not identifier.strip():
        return None, "invalid_id"
    identifier = identifier.strip()
    versions = record.get("versions")
    if not isinstance(versions, list):
        return None, "missing_v1"
    first = next((v for v in versions if isinstance(v, dict)
                  and v.get("version") == "v1"), None)
    if first is None:
        return None, "missing_v1"
    try:
        raw_date = first.get("created")
        if not isinstance(raw_date, str):
            raise ValueError("date non textuelle")
        submitted = parsedate_to_datetime(raw_date)
        if submitted.tzinfo is None:
            submitted = submitted.replace(tzinfo=timezone.utc)
        day = submitted.astimezone(timezone.utc).date()
    except (ValueError, TypeError, OverflowError):
        return None, "invalid_v1_date"
    if not start_year <= day.year <= end_year:
        return None, "outside_years"
    raw_categories = record.get("categories")
    if not isinstance(raw_categories, str) or not raw_categories.strip():
        return None, "invalid_categories"
    categories = list(dict.fromkeys(raw_categories.split()))
    selected = [c for c in categories if c in allowed_categories]
    if not selected:
        return None, "outside_categories"
    return {
        "id": identifier,
        "title": clean_text(record.get("title")),
        "abstract": clean_text(record.get("abstract")),
        "authors": clean_text(record.get("authors")),
        "submitted_at": day,
        "year": day.year,
        "categories": categories,
        "selected_categories": selected,
        "arxiv_url": "https://arxiv.org/abs/" + quote(identifier, safe="/"),
    }, None


def prepare(input_path, output_path, *, start_year=2020, end_year=2024,
            categories=("cs.AI", "cs.LG", "cs.CL"), batch_size=10000,
            source_version="unspecified"):
    """Produit les fichiers et retourne le rapport de qualité.

    Une ligne reçoit exactement une issue. Parmi les articles admissibles,
    la première occurrence d'un identifiant est conservée. Les fichiers existants
    ne sont remplacés qu'après lecture et écriture complètes dans un dossier temporaire.
    """
    input_path, output_path = Path(input_path), Path(output_path)
    report_path = output_path.with_suffix(".quality.json")
    if not 1 <= start_year <= end_year <= 9999:
        raise ValueError("Les années doivent vérifier 1 <= début <= fin <= 9999.")
    if batch_size < 1:
        raise ValueError("La taille des blocs doit être positive.")
    allowed = set(categories)
    if not allowed or any(not isinstance(c, str) or not c.strip() for c in allowed):
        raise ValueError("Choisir au moins une catégorie non vide.")
    if output_path.suffix != ".parquet":
        raise ValueError("La sortie doit avoir l'extension .parquet.")
    if input_path.resolve() in (output_path.resolve(), report_path.resolve()):
        raise ValueError("La source ne doit pas être une destination de sortie.")
    counts = Counter({reason: 0 for reason in REASONS})
    missing_text = Counter({field: 0 for field in ("title", "abstract", "authors")})
    seen, batch = set(), []
    digest = hashlib.sha256()
    lines = 0
    # Ouvrir la source avant de créer les destinations : erreur claire si absente.
    with input_path.open("rb") as source:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".arxiv-", dir=output_path.parent) as temp:
            staged_output = Path(temp) / "articles.parquet"
            with pq.ParquetWriter(staged_output, SCHEMA, compression="snappy") as writer:
                for raw in source:
                    digest.update(raw)
                    lines += 1
                    if not raw.strip():
                        counts["blank_lines"] += 1
                        continue
                    try:
                        record = json.loads(raw)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        counts["invalid_json"] += 1
                        continue
                    article, reason = normalize(record, start_year, end_year, allowed)
                    if reason:
                        counts[reason] += 1
                        continue
                    if article["id"] in seen:
                        counts["duplicate_retained_id"] += 1
                        continue
                    seen.add(article["id"])
                    counts["retained"] += 1
                    for field in missing_text:
                        if not article[field]:
                            missing_text[field] += 1
                    batch.append(article)
                    if len(batch) >= batch_size:
                        writer.write_table(pa.Table.from_pylist(batch, schema=SCHEMA))
                        batch.clear()
                if batch:
                    writer.write_table(pa.Table.from_pylist(batch, schema=SCHEMA))
            report = {
                "schema_version": 1,
                "source": {
                    "filename": input_path.name,
                    "version": source_version,
                    "sha256": digest.hexdigest(),
                },
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "runtime": {"python": platform.python_version(), "pyarrow": pa.__version__},
                "parameters": {"start_year": start_year, "end_year": end_year,
                               "categories": sorted(allowed), "batch_size": batch_size},
                "lines_read": lines,
                "outcomes": dict(counts),
                "missing_text_in_retained": dict(missing_text),
                "output_filename": output_path.name,
            }
            staged_report = Path(temp) / "quality.json"
            staged_report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                                     encoding="utf-8")
            staged_output.replace(output_path)
            staged_report.replace(report_path)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Snapshot JSONL décompressé")
    parser.add_argument("--output", type=Path, required=True, help="Destination .parquet")
    parser.add_argument("--start-year", type=int, default=2020)
    parser.add_argument("--end-year", type=int, default=2024)
    parser.add_argument("--categories", nargs="+", default=["cs.AI", "cs.LG", "cs.CL"])
    parser.add_argument("--batch-size", type=int, default=10000)
    parser.add_argument("--source-version", required=True, help="Version Kaggle ou synthetic-demo-v1")
    args = parser.parse_args()
    try:
        report = prepare(args.input, args.output, start_year=args.start_year,
                         end_year=args.end_year, categories=args.categories,
                         batch_size=args.batch_size, source_version=args.source_version)
    except (OSError, ValueError, pa.ArrowException) as error:
        parser.exit(2, f"Erreur : {error}\n")
    print(json.dumps({"lines_read": report["lines_read"], **report["outcomes"]},
                     ensure_ascii=False, indent=2))
    print(f"Données : {args.output}\nRapport : {args.output.with_suffix('.quality.json')}")


if __name__ == "__main__":
    main()
