"""Contenu des quatre onglets de l'application."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from ui.data import DataSource
from ui.filters import Filters, available_categories

MAX_ROWS = 50
SOURCE_URL = "https://www.kaggle.com/datasets/Cornell-University/arxiv"
NO_TITLE = "(sans titre)"
EMPTY_MESSAGE = (
    "Aucun article ne correspond à ces filtres. Élargissez la période ou "
    "retirez une catégorie."
)


def format_count(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def results_table(shown: pd.DataFrame, source: DataSource) -> pd.DataFrame:
    table = pd.DataFrame(
        {
            "Titre": shown["title"].where(shown["title"] != "", NO_TITLE),
            "Auteurs": shown["authors"],
            "Premier dépôt": shown["submitted_at"],
            "Catégories étudiées": shown["selected_categories"].map(", ".join),
        }
    )
    # Les identifiants de la démonstration sont fictifs : leurs liens ne mènent nulle part.
    if not source.is_demo:
        table["Lien"] = shown["arxiv_url"]
    return table


def overview(filtered: pd.DataFrame, filters: Filters) -> None:
    total = filtered["id"].nunique()
    left, middle, right = st.columns(3)
    left.metric("Articles uniques", format_count(total))
    middle.metric("Période filtrée", f"{filters.year_min} à {filters.year_max}")
    right.metric("Catégories étudiées", len(available_categories(filtered)))
    if total == 0:
        st.warning(EMPTY_MESSAGE)
        return
    st.caption(
        "Un article est compté une seule fois, même s'il porte plusieurs catégories."
    )


def comparison(filtered: pd.DataFrame) -> None:
    if filtered.empty:
        st.warning(EMPTY_MESSAGE)
        return
    st.caption(
        "Un article peut porter plusieurs catégories : la somme des catégories "
        "dépasse le nombre d'articles uniques."
    )


def exploration(filtered: pd.DataFrame, source: DataSource) -> None:
    total = filtered["id"].nunique()
    if total == 0:
        st.warning(EMPTY_MESSAGE)
        return
    shown = filtered.sort_values(["submitted_at", "id"], ascending=[False, True]).head(MAX_ROWS)
    st.write(
        f"{format_count(total)} articles correspondent aux filtres ; "
        f"les {len(shown)} plus récents sont affichés."
    )
    st.dataframe(
        results_table(shown, source),
        hide_index=True,
        width="stretch",
        column_config={
            "Premier dépôt": st.column_config.DateColumn(format="DD/MM/YYYY"),
            "Lien": st.column_config.LinkColumn(display_text="Ouvrir sur arXiv"),
        },
    )


def method(articles: pd.DataFrame, source: DataSource) -> None:
    first_year, last_year = int(articles["year"].min()), int(articles["year"].max())
    st.markdown(
        f"""
**Source.** Métadonnées arXiv publiées par Cornell University sur Kaggle :
[{SOURCE_URL}]({SOURCE_URL}). Seul le fichier de métadonnées est utilisé, pas les PDF.

**Fichier chargé.** `{source.path}`, {format_count(articles["id"].nunique())} articles,
premier dépôt de {first_year} à {last_year}, catégories étudiées :
{", ".join(available_categories(articles))}.

**Règles.**
- Un article est identifié par son `id` arXiv et compté une seule fois.
- La date est celle du premier dépôt (version v1), jamais la date de mise à jour.
- Un article portant plusieurs catégories compte une fois au total et une fois
  dans chacune de ses catégories.
- Plusieurs catégories sélectionnées : un article est retenu si au moins une de
  ses catégories est sélectionnée. Aucune catégorie sélectionnée signifie « toutes ».

**Limites.**
- Davantage de dépôts ne prouve pas une meilleure qualité scientifique.
- Le périmètre (catégories et années ci-dessus) ne représente pas toute la
  recherche mondiale, ni tout arXiv.
- Aucune mesure de citations ou d'impact n'est disponible dans ces données.

Le détail des règles de préparation est dans `docs/methodology.md`.
"""
    )
