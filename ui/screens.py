"""Contenu des quatre onglets de l'application."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.metrics import category_share, unique_articles, yearly_change
from ui.charts import annual_chart, category_chart, growth_chart
from ui.design import section_intro
from ui.showcase import save_article
from ui.data import DataSource
from ui.export import file_name, to_csv_bytes
from ui.filters import Filters, available_categories

PAGE_SIZE = 25
SOURCE_URL = "https://www.kaggle.com/datasets/Cornell-University/arxiv"
NO_TITLE = "(sans titre)"
EMPTY_MESSAGE = (
    "Aucun article ne correspond à ces filtres. Élargissez la période, retirez "
    "une catégorie ou modifiez la recherche."
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
    section_intro("VUE D’ENSEMBLE", "La recherche, en perspective.",
                  "Les indicateurs de votre sélection, du premier dépôt aux tendances annuelles.")
    total = unique_articles(filtered)
    annual = yearly_change(filtered, year_range=(filters.year_min, filters.year_max))
    last = annual.iloc[-1]
    change = last["change_pct"]
    left, middle, right, growth = st.columns(4)
    left.metric("Articles uniques", format_count(total))
    middle.metric("Période filtrée", f"{filters.year_min} à {filters.year_max}")
    right.metric("Catégories étudiées", len(available_categories(filtered)))
    growth.metric(f"Variation en {int(last['year'])}",
                  "Non calculable" if pd.isna(change) else f"{change:+.2f} %")
    if total == 0:
        st.warning(EMPTY_MESSAGE)
        return
    st.caption("Un article est compté une seule fois, même s'il porte plusieurs catégories.")
    trend_column, growth_column = st.columns([1.65, 1], gap="medium")
    with trend_column, st.container(border=True, key="trend_panel"):
        st.subheader("Dépôts par année")
        st.caption("L’évolution du volume d’articles dans votre sélection.")
        st.plotly_chart(annual_chart(annual), width="stretch", key="annual_chart", theme=None)
    with growth_column, st.container(border=True, key="growth_panel"):
        st.subheader("Variation annuelle")
        st.caption("Le rythme d’évolution par rapport à l’année précédente.")
        if annual["change_pct"].notna().any():
            st.plotly_chart(growth_chart(annual), width="stretch", key="growth_chart", theme=None)
        else:
            st.info("Aucune variation annuelle calculable pour cette sélection.")
    st.caption(
        "Variation = (N − N précédent) / N précédent × 100. La première année "
        "affichée et les années dont la base est nulle sont non calculables. "
        "Les années sans résultat dans la période couverte valent zéro."
    )
    with st.expander("Voir les chiffres annuels"):
        table = annual.rename(columns={"year": "Année", "articles": "Articles uniques",
                                       "change_pct": "Variation (%)"})
        st.dataframe(table, hide_index=True, width="stretch")


def comparison(filtered: pd.DataFrame) -> None:
    section_intro("REGARDS CROISÉS", "Trois domaines. Des liens multiples.",
                  "Comparez les catégories et leur place dans les articles sélectionnés.")
    if filtered.empty:
        st.warning(EMPTY_MESSAGE)
        return
    st.subheader("Comparer les catégories")
    shares = category_share(filtered)
    st.plotly_chart(category_chart(shares), width="stretch", key="category_chart", theme=None)
    st.caption(
        "Un article peut porter plusieurs catégories : la somme peut dépasser "
        "le nombre d'articles uniques, et les parts peuvent dépasser 100 % au total. "
        "Chaque part utilise le total des articles filtrés comme dénominateur. "
        "Toutes les catégories étudiées des articles retenus sont montrées : "
        "un filtre cs.AI peut aussi faire apparaître cs.LG pour un article commun."
    )
    st.dataframe(
        shares.rename(columns={"category": "Catégorie", "articles": "Articles uniques",
                               "share_pct": "Part des articles (%)"}),
        hide_index=True, width="stretch",
    )


def page_count(total: int) -> int:
    return max(1, -(-total // PAGE_SIZE))


def article_label(article: pd.Series) -> str:
    return f"{article['title'] or NO_TITLE} ({article['year']})"


def article_detail(article: pd.Series, source: DataSource, *, location="explore") -> None:
    """Fiche d'un article : titre, auteurs, date, catégories, résumé, lien."""
    with st.container(border=True):
        st.subheader(article["title"] or NO_TITLE)
        st.write(article["authors"] or "Auteurs non renseignés")
        st.markdown(
            f"**Premier dépôt (v1) :** {article['submitted_at']:%d/%m/%Y}  \n"
            f"**Catégories étudiées :** {', '.join(article['selected_categories'])}  \n"
            f"**Toutes les catégories :** {', '.join(article['categories'])}  \n"
            f"**Identifiant arXiv :** {article.name}"
        )
        st.write(article["abstract"] or "Résumé non disponible dans les données.")
        if source.is_demo:
            st.caption("Article fictif de démonstration : il n'existe pas sur arXiv.")
        else:
            st.link_button("Ouvrir sur arXiv", article["arxiv_url"])
        saved=article.name in st.session_state.get('reading_ids',[])
        st.button('Déjà dans le panier' if saved else 'Ajouter au panier de lecture',
                  on_click=save_article,args=(article.name,),disabled=saved,
                  key=f'save_{location}_{article.name}')


def exploration(filtered: pd.DataFrame, filters: Filters, source: DataSource) -> None:
    section_intro("BIBLIOTHÈQUE DE RECHERCHE", "Votre prochain point de départ.",
                  "Parcourez les publications, explorez un résumé et emportez votre sélection.")
    total = filtered["id"].nunique()
    if total == 0:
        st.warning(EMPTY_MESSAGE)
        return

    if st.button("Découvrir un article au hasard",key='random_article'):
        st.session_state['spotlight_id']=filtered.sample(1)['id'].iloc[0]
    spotlight=st.session_state.get('spotlight_id')
    if spotlight in set(filtered['id']):
        with st.expander("Votre découverte inattendue",expanded=True):
            article_detail(filtered.set_index('id').loc[spotlight],source,location='spotlight')

    ordered = filtered.sort_values(["submitted_at", "id"], ascending=[False, True])
    pages = page_count(total)
    summary, pager = st.columns([3, 1])
    page = 1
    if pages > 1:
        page = pager.number_input("Page", min_value=1, max_value=pages, value=1, key="page")
    start = (page - 1) * PAGE_SIZE
    shown = ordered.iloc[start : start + PAGE_SIZE]
    summary.write(
        f"{format_count(total)} articles correspondent aux filtres, du plus récent au plus "
        f"ancien. Articles {start + 1} à {start + len(shown)}, page {page} sur {pages}."
    )
    st.dataframe(
        results_table(shown, source),
        hide_index=True,
        width="stretch",
        column_config={
            "Titre": st.column_config.TextColumn(width="large"),
            "Auteurs": st.column_config.TextColumn(width="medium"),
            "Premier dépôt": st.column_config.DateColumn(format="DD/MM/YYYY"),
            "Lien": st.column_config.LinkColumn(display_text="Ouvrir sur arXiv"),
        },
    )

    by_id = shown.set_index("id")
    chosen = st.selectbox(
        "Fiche d'un article de cette page",
        options=list(by_id.index),
        format_func=lambda article_id: article_label(by_id.loc[article_id]),
        index=None,
        placeholder="Choisir un article",
        key="detail",
    )
    if chosen is not None and chosen in by_id.index:
        article_detail(by_id.loc[chosen], source)

    st.download_button(
        f"Exporter les {format_count(total)} articles filtrés (CSV)",
        data=lambda: to_csv_bytes(filtered),
        file_name=file_name(filters),
        mime="text/csv",
        key="export",
    )
    st.caption(
        "L'export contient tous les articles filtrés, pas seulement la page affichée : "
        "une ligne par article, catégories séparées par « ; »."
    )


def method(articles: pd.DataFrame, source: DataSource) -> None:
    section_intro("EN TOUTE TRANSPARENCE", "Comprendre ce que disent les données.",
                  "Une source documentée, des règles explicites et des limites à connaître.")
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
- La recherche porte sur les titres et les résumés. Elle cherche l'expression
  exacte, sans tenir compte des majuscules.
- L'export CSV contient exactement les articles filtrés, une ligne par article.

**Limites.**
- Davantage de dépôts ne prouve pas une meilleure qualité scientifique.
- Le périmètre (catégories et années ci-dessus) ne représente pas toute la
  recherche mondiale, ni tout arXiv.
- Aucune mesure de citations ou d'impact n'est disponible dans ces données.

Le détail des règles de préparation est dans `docs/methodology.md`.
"""
    )
