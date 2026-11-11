"""arXiv Explorer : point d'entrée de l'application Streamlit.

Lancement : python -m streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from ui import screens, showcase
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


def preset(name, first, last):
    st.session_state['categories'] = ['cs.CL'] if name == 'Transformer' else []
    st.session_state['query'] = 'transformer' if name == 'Transformer' else ''
    if first != last:
        st.session_state['years'] = (max(first, min(2023,last)),last) if name == 'Transformer' else (first,last)
    for key in ('page','detail'):
        st.session_state.pop(key,None)


def sidebar_filters(articles) -> Filters:
    first_year, last_year = year_bounds(articles)
    sidebar_brand()
    with st.sidebar.expander("Scénarios en un clic", expanded=False):
        st.button("Panorama · tout le corpus",on_click=preset,args=('Panorama',first_year,last_year),key='preset_all',width='stretch')
        st.button("Enquête · transformer",on_click=preset,args=('Transformer',first_year,last_year),key='preset_transformer',width='stretch')
        st.caption("Les scénarios modifient les filtres communs. Parcourez ensuite les onglets.")
    presentation=st.sidebar.toggle("Mode projection",key='presentation_mode')
    if presentation:
        st.markdown('<style>.stMainBlockContainer{max-width:1800px}.section-intro h2{font-size:2rem}[data-testid="stCaptionContainer"] p{font-size:.9rem}.research-hero{min-height:0;padding:24px 35px}.research-hero h1{font-size:2rem}.orbit-art{display:none}.hero-tags{margin-top:12px}</style>',unsafe_allow_html=True)
    st.sidebar.header("Affiner l'exploration")
    if first_year == last_year:
        years = (first_year, last_year)
        st.sidebar.write(f"Année de premier dépôt : {first_year}")
    else:
        if "years" not in st.session_state:
            st.session_state["years"] = (first_year, last_year)
        years = st.sidebar.slider(
            "Années de premier dépôt",
            min_value=first_year,
            max_value=last_year,

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

    overview_tab, trends_tab, comparison_tab, vocabulary_tab, exploration_tab, reading_tab, workshop_tab, method_tab = st.tabs(
        ["Vue d'ensemble", "Tendances", "Comparaison", "Vocabulaire", "Exploration", "Panier de lecture", "Atelier", "Méthode"], key=f"workspace_{st.session_state.get('workspace_token',0)}", default=st.session_state.get("workspace","Vue d'ensemble"), on_change="ignore"
    )
    with overview_tab:
        screens.overview(filtered, filters)
        showcase.overview_atlas(filtered, filters)
    with trends_tab:
        showcase.trends(filtered, filters)
    with comparison_tab:
        screens.comparison(filtered)
        showcase.connections(filtered)
    with vocabulary_tab:
        showcase.vocabulary(filtered, filters)
    with exploration_tab:
        screens.exploration(filtered, filters, source)
    with reading_tab:
        showcase.reading_list(articles, source)
    with workshop_tab:
        showcase.workshop()
    with method_tab:
        screens.method(articles, source)
    st.markdown('<div class="app-footer"><span>arXiv Explorer · Les données au service des idées.</span>'
                '<span>Démonstrateur pédagogique · BI · Python · GitHub</span></div>', unsafe_allow_html=True)


main()
