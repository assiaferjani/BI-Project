"""Vérifie le contrat du Parquet et produit un bilan BI reproductible."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import pyarrow as pa

from src.metrics import category_share, unique_articles, yearly_change
from src.prepare_data import SCHEMA


def valid_codes(value):
    return (
        pd.api.types.is_list_like(value)
        and len(value) > 0
        and all(isinstance(code, str) and bool(code.strip()) for code in value)
        and len(set(value)) == len(value)
    )


def build_profile(frame: pd.DataFrame) -> dict:
    """Refuse un contrat incohérent avant de calculer le bilan.

    Le bilan décrit uniquement les articles présents. Les années absentes ne
    sont pas converties implicitement en zéro. Il ne contient aucun résumé.
    """
    missing = [field for field in SCHEMA.names if field not in frame.columns]
    if missing:
        raise ValueError("Colonnes manquantes : " + ", ".join(missing))
    dates = pd.to_datetime(frame["submitted_at"], errors="coerce")
    checks = {
        "ids_nonempty_strings": bool(frame["id"].map(
            lambda value: isinstance(value, str) and bool(value.strip())
        ).all()),
        "ids_unique": not frame["id"].duplicated().any(),
        "dates_valid": bool(dates.notna().all()),
        "year_matches_submission": bool(
            dates.dt.year.eq(pd.to_numeric(frame["year"], errors="coerce")).all()
        ),
        "categories_valid": bool(frame["categories"].map(valid_codes).all()),
        "selected_categories_valid": bool(frame["selected_categories"].map(valid_codes).all()),
        "text_fields_are_strings": all(
            frame[field].map(lambda value: isinstance(value, str)).all()
            for field in ("title", "abstract", "authors")
        ),
    }
    if checks["categories_valid"] and checks["selected_categories_valid"]:
        checks["selected_categories_in_original"] = all(
            set(selected).issubset(original)
            for selected, original in zip(frame["selected_categories"], frame["categories"])
        )
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError("Contrôles en échec : " + ", ".join(failed))
    shares = category_share(frame)
    annual = yearly_change(frame)
    return {
        "rows": len(frame),
        "unique_articles": unique_articles(frame),
        "checks": checks,
        "first_submission": dates.min().date().isoformat() if len(frame) else None,
        "last_submission": dates.max().date().isoformat() if len(frame) else None,
        "missing_text": {
            field: int(frame[field].str.strip().eq("").sum())
            for field in ("title", "abstract", "authors")
        },
        "articles_with_multiple_selected_categories": int(
            frame["selected_categories"].map(len).gt(1).sum()
        ),
        "category_memberships": int(shares["articles"].sum()),
        # pandas sérialise les NaN en null : le JSON produit reste standard.
        "annual": json.loads(annual.to_json(orient="records")),
        "categories": json.loads(shares.to_json(orient="records")),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        parser.error("Le rapport ne doit pas remplacer le fichier source.")
    try:
        report = build_profile(pd.read_parquet(args.input))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
    except (OSError, ValueError, pa.ArrowException) as error:
        parser.exit(2, f"Erreur : {error}\n")
    print(f"{report['unique_articles']} articles uniques ; contrat vérifié.")
    print(f"Bilan : {args.output}")


if __name__ == "__main__":
    main()
