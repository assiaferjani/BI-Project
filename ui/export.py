"""Export CSV des résultats filtrés."""

from __future__ import annotations

import pandas as pd

from ui.filters import Filters
from ui.search import clean_query

SEPARATOR = " ; "


def export_table(filtered: pd.DataFrame) -> pd.DataFrame:
    """Table exportée : une ligne par article, colonnes lisibles, listes aplaties."""
    table = pd.DataFrame(
        {
            "id": filtered["id"],
            "titre": filtered["title"],
            "auteurs": filtered["authors"],
            "date_premier_depot": filtered["submitted_at"],
            "annee": filtered["year"],
            "categories_etudiees": filtered["selected_categories"].map(SEPARATOR.join),
            "toutes_les_categories": filtered["categories"].map(SEPARATOR.join),
            "resume": filtered["abstract"],
            "lien_arxiv": filtered["arxiv_url"],
        }
    )
    return table.sort_values(["date_premier_depot", "id"]).reset_index(drop=True)


def to_csv_bytes(filtered: pd.DataFrame) -> bytes:
    """CSV encodé en UTF-8 avec BOM, pour s'ouvrir correctement dans un tableur."""
    return export_table(filtered).to_csv(index=False).encode("utf-8-sig")


def file_name(filters: Filters) -> str:
    """Nom de fichier qui rappelle les filtres appliqués."""
    parts = ["arxiv_explorer", f"{filters.year_min}-{filters.year_max}", *filters.categories]
    words = "".join(c if c.isalnum() else "-" for c in clean_query(filters.query).casefold())
    slug = "-".join(filter(None, words.split("-")))[:40]
    if slug:
        parts.append(slug)
    return "_".join(parts) + ".csv"
