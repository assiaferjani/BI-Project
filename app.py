"""arXiv Explorer : point d'entrée de l'application Streamlit.

Lancement : python -m streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from ui import screens
from ui.design import apply_design, hero, sidebar_brand
from ui.data import DataError, find_source, load_articles
from ui.filters import Filters, apply_filters, available_categories, year_bounds

st.set_page_config(page_title="arXiv Explorer · Observatoire de la recherche", page_icon="◈", layout="wide")
apply_design()


@st.cache_resource(show_spinner="Chargement des articles…")
def cached_articles(path: str, modified: float):
    # Table partagée entre les sessions et jamais modifiée après chargement.
    # `modified` invalide le cache quand le fichier préparé est régénéré.
    return load_articles(path)


def sidebar_filters(articles) -> Filters:
    first_year, last_year = year_bounds(articles)
    sidebar_brand()
    st.sidebar.header("Affiner l'exploration")
    if first_year == last_year:
        years = (first_year, last_year)
        st.sidebar.write(f"Année de premier dépôt : {first_year}")
    else:
        years = st.sidebar.slider(
            "Années de premier dépôt",
            min_value=first_year,
            max_value=last_year,
            value=(first_year, last_year),
            key="years",
        )
    categories = st.sidebar.multiselect(
        "Catégories",
        options=available_categories(articles),
        placeholder="Toutes les catégories",
        help="Un article est retenu si au moins une de ses catégories est sélectionnée. "
        "Sans sélection, toutes les catégories sont gardées.",
        key="categories",
    )
    query = st.sidebar.text_input(
        "Recherche",
        placeholder="Mot ou expression",
        help="Cherche l'expression exacte dans les titres et les résumés, "
        "sans tenir compte des majuscules.",
        key="query",
    )
    st.sidebar.markdown('<div class="sidebar-rule"></div>', unsafe_allow_html=True)
    st.sidebar.caption("Trois domaines, une perspective commune.")
    st.sidebar.caption("cs.AI · Intelligence artificielle\n\ncs.LG · Apprentissage automatique\n\ncs.CL · Traitement du langage")
    return Filters(
        year_min=years[0], year_max=years[1], categories=tuple(categories), query=query
    )


def main() -> None:
    try:
        source = find_source()
        articles = cached_articles(str(source.path), source.path.stat().st_mtime)
    except DataError as error:
        st.error(str(error))
        st.stop()

    if articles.empty:
        st.error(f"Le fichier {source.path} ne contient aucun article.")
        st.stop()

    first, last = year_bounds(articles)
    hero(len(articles), first, last, is_demo=source.is_demo)

    if source.is_demo:
        st.warning(
            f"Données fictives de démonstration : {len(articles)} articles inventés. "
            "Les chiffres affichés ne sont pas des résultats et les articles n'existent "
            "pas sur arXiv. Préparez le vrai fichier avec la commande du README."
        )

    filters = sidebar_filters(articles)
    filtered = apply_filters(articles, filters)

    overview_tab, comparison_tab, exploration_tab, method_tab = st.tabs(
        ["Vue d'ensemble", "Comparaison", "Exploration", "Méthode"]
    )
    with overview_tab:
        screens.overview(filtered, filters)
    with comparison_tab:
        screens.comparison(filtered)
    with exploration_tab:
        screens.exploration(filtered, filters, source)
    with method_tab:
        screens.method(articles, source)
    st.markdown('<div class="app-footer"><span>arXiv Explorer · Les données au service des idées.</span>'
                '<span>Assia Ferjani &amp; Ines Makhlouf · Projet BI</span></div>', unsafe_allow_html=True)


main()
