"""Indicateurs BI sur la table déjà filtrée, sans modifier les articles.

Le contrat de colonnes est celui de docs/data_dictionary.md. Les fonctions
acceptent les listes/arrays Parquet comme les tuples du chargeur de l'interface.
"""

from __future__ import annotations

import pandas as pd


def unique_articles(df: pd.DataFrame) -> int:
    """Nombre d'identifiants distincts dans les résultats filtrés."""
    return int(df["id"].nunique())


def submissions_per_year(
    df: pd.DataFrame, *, year_range: tuple[int, int] | None = None
) -> pd.DataFrame:
    """Table year/articles, triée par année, un id compté une fois par année.

    Sans year_range, seules les années présentes sont retournées. Avec une
    période explicitement couverte par les données, les années sans résultat
    reçoivent zéro. Une période ne contenant pas tous les résultats est refusée.
    """
    counts = df.groupby("year")["id"].nunique().sort_index()
    if year_range is not None:
        first, last = year_range
        if not 1 <= first <= last <= 9999:
            raise ValueError("La période doit vérifier 1 <= début <= fin <= 9999.")
        if not counts.index.to_series().between(first, last).all():
            raise ValueError("Filtrer les articles dans la période avant le calcul.")
        counts = counts.reindex(range(first, last + 1), fill_value=0)
    return (
        counts.rename_axis("year")
        .rename("articles")
        .reset_index()
        .astype({"year": "int64", "articles": "int64"})
    )


def articles_per_category(df: pd.DataFrame) -> pd.DataFrame:
    """Table category/articles des catégories étudiées présentes, triée par code.

    Un article compte dans chacune de ses selected_categories. Les répétitions
    d'une catégorie ou d'un id ne gonflent pas le compte de cette catégorie.
    Le filtre choisit des articles : on conserve toutes leurs catégories étudiées.
    """
    expanded = df[["id", "selected_categories"]].explode("selected_categories")
    counts = expanded.groupby("selected_categories")["id"].nunique().sort_index()
    return (
        counts.rename_axis("category")
        .rename("articles")
        .reset_index()
        .astype({"category": "str", "articles": "int64"})
    )


def category_share(df: pd.DataFrame) -> pd.DataFrame:
    """Part de chaque catégorie dans les articles uniques filtrés, en pourcent.

    Les parts ne sont pas une répartition exclusive : leur somme peut dépasser
    100 %. Un résultat vide retourne une table vide avec les colonnes attendues.
    """
    result = articles_per_category(df)
    total = unique_articles(df)
    result["share_pct"] = result["articles"] * 100.0 / total if total else float("nan")
    return result


def yearly_change(
    df: pd.DataFrame, *, year_range: tuple[int, int] | None = None
) -> pd.DataFrame:
    """Variation face à l'année civile précédente, jamais la précédente ligne.

    change_pct est NaN lorsque la base manque ou vaut zéro. La première année
    de la période n'utilise pas de données hors filtres. Voir submissions_per_year
    pour l'option year_range et les années explicitement remplies par zéro.
    """
    result = submissions_per_year(df, year_range=year_range)
    counts = result.set_index("year")["articles"]
    previous = pd.Series(
        counts.reindex(result["year"] - 1).to_numpy(), index=result.index, dtype="float64"
    )
    denominator = previous.where(previous.ne(0))
    result["change_pct"] = (result["articles"] - previous) / denominator * 100.0
    return result
