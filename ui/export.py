"""Export CSV des résultats filtrés."""

from __future__ import annotations

import pandas as pd

from ui.data import AUDIO_FEATURES
from ui.filters import Filters
from ui.search import normalize

SEPARATOR = " ; "


def export_table(filtered: pd.DataFrame) -> pd.DataFrame:
    """Table exportée : une ligne par titre, colonnes lisibles, listes aplaties."""
    table = pd.DataFrame(
        {
            "id": filtered["id"],
            "titre": filtered["name"],
            "artistes": filtered["artists"].map(SEPARATOR.join),
            "annee": filtered["year"],
            "date_sortie": filtered["release_date"],
            "familles_de_genres": filtered["selected_genres"].map(SEPARATOR.join),
            "popularite": filtered["popularity"],
            "duree_ms": filtered["duration_ms"],
            "explicite": filtered["explicit"].map({True: "oui", False: "non"}),
        }
    )
    for feature in AUDIO_FEATURES:
        table[feature] = filtered[feature]
    table["lien_spotify"] = filtered["spotify_url"]
    return table.sort_values(["annee", "id"]).reset_index(drop=True)


def to_csv_bytes(filtered: pd.DataFrame) -> bytes:
    """CSV encodé en UTF-8 avec BOM, pour s'ouvrir correctement dans un tableur."""
    return export_table(filtered).to_csv(index=False).encode("utf-8-sig")


def file_name(filters: Filters) -> str:
    """Nom de fichier qui rappelle les filtres appliqués."""
    parts = ["spotify_explorer", f"{filters.year_min}-{filters.year_max}"]
    parts += [genre.replace(" ", "-") for genre in filters.genres]
    if filters.query.strip():
        words = "".join(c if c.isalnum() else "-" for c in normalize(filters.query))
        parts.append("-".join(filter(None, words.split("-")))[:40] or "recherche")
    return "_".join(parts) + ".csv"
