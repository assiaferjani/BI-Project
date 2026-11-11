"""Outils partagés par les tests de l'interface."""

import json
from pathlib import Path

from src.prepare_data import prepare
from ui.data import DEMO_PATH

REPO_ROOT = Path(__file__).resolve().parents[1]
DEMO_SOURCE = REPO_ROOT / "data" / "sample" / "arxiv_demo.jsonl"

CYCLE = ["cs.AI", "cs.LG", "cs.CL", "cs.AI cs.LG", "cs.CL stat.ML"]


def controlled_records(count: int = 60) -> list[dict]:
    """Articles fictifs réguliers : 12 par année de 2020 à 2024, catégories en cycle."""
    records = []
    for index in range(count):
        year = 2020 + index % 5
        records.append(
            {
                "id": f"test-{index:03d}",
                "title": f"Article {index:03d} about {'Transformers' if index % 4 == 0 else 'graphs'}",
                "abstract": "" if index == 7 else f"We study topic number {index} (résumé d'essai).",
                "authors": f"Author {index}, Coauthor {index}",
                "categories": CYCLE[index % len(CYCLE)],
                "versions": [
                    {"version": "v1", "created": f"Mon, {1 + index % 28:02d} Mar {year} 10:00:00 GMT"}
                ],
            }
        )
    return records


def prepare_workspace(root: Path, source: Path | None = None, records: list[dict] | None = None) -> Path:
    """Crée dans `root` le fichier de démonstration, avec le vrai pipeline du projet."""
    if records is not None:
        source = root / "controlled.jsonl"
        source.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
    output = root / DEMO_PATH
    prepare(source or DEMO_SOURCE, output, source_version="test")
    return output
