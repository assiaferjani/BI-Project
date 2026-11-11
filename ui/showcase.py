"""Parcours d'exploration et interactions pour une démonstration en classe."""
import pandas as pd
import streamlit as st

from src.discovery import (monthly_counts, category_trajectories, category_overlap,
    category_combinations, title_vocabulary, term_trajectory)
from ui import discovery_charts as charts
from ui.design import section_intro
from ui.export import to_csv_bytes


def question(prompt, answer, key):
    with st.expander('À vous de jouer · ' + prompt):
        st.write('Formulez une hypothèse, explorez les graphiques, puis confrontez-la aux chiffres.')
        if st.checkbox('Révéler une piste de réponse',key=key):
            st.info(answer)


def trends(frame, filters):
    section_intro('LE TEMPS DE LA RECHERCHE', 'Les tendances ne sont pas toutes linéaires.',
        'Changez d’échelle et distinguez volume, rythme et trajectoire relative.')
    if frame.empty:
        st.info('Aucun article dans cette sélection. Modifiez les filtres à gauche.')
        return
    table=monthly_counts(frame,filters.year_min,filters.year_max)
    with st.container(border=True):
        st.subheader('Quand les idées arrivent-elles ?')
        percent=st.toggle('Comparer la répartition mensuelle en %',key='calendar_percent')
        st.plotly_chart(charts.heatmap(table,percent=percent),theme=None,width='stretch',key='calendar_chart')
        st.caption('Une case = un mois de premier dépôt. En %, chaque ligne totalise 100 % si son année contient des articles. Les cases vides ne constituent pas une preuve de saisonnalité.')
    left,right=st.columns([1.3,1],gap='medium')
    with left,st.container(border=True):
        st.subheader('Qui progresse le plus vite ?')
        indexed=st.toggle('Comparer en base 100',key='indexed_categories')
        trajectories=category_trajectories(frame,filters.year_min,filters.year_max)
        st.plotly_chart(charts.trajectories(trajectories,indexed=indexed),theme=None,width='stretch',key='trajectories_chart')
        st.caption('Base 100 = première année filtrée. Une catégorie à zéro cette année-là est non calculable. Les catégories peuvent partager des articles.')
    with right,st.container(border=True):
        st.subheader('Le calendrier des dépôts')
        st.plotly_chart(charts.seasonality(table),theme=None,width='stretch',key='seasonality_chart')
        st.caption('Somme par mois sur toutes les années sélectionnées, sans correction de durée des mois ni des années partielles.')
    peak=table.sum(axis=0).idxmax()
    question('Quel mois concentre le plus de dépôts ?',
        f'Dans votre sélection : {charts.MONTHS[peak-1]}, avec {int(table.sum(axis=0).max()):,} articles. Une observation descriptive, pas une explication causale.', 'calendar_answer')


def connections(frame):
    section_intro('LES FRONTIÈRES SONT POREUSES', 'Les domaines se rencontrent.',
        'Une autre lecture des catégories : des ensembles qui se recouvrent, plutôt que des cases indépendantes.')
    if frame.empty:
        return
    left,right=st.columns(2,gap='medium')
    with left,st.container(border=True):
        st.subheader('La carte des recouvrements')
        normalized=st.toggle('Normaliser avec l’indice de Jaccard',key='overlap_normalized')
        matrix=category_overlap(frame,normalized=normalized)
        st.plotly_chart(charts.overlap_chart(matrix,percent=normalized),theme=None,width='stretch',key='overlap_chart')
        st.caption('Effectif = articles partagés. Jaccard = intersection / union × 100. La diagonale vaut l’effectif de la catégorie, ou 100 % en Jaccard.')
    with right,st.container(border=True):
        st.subheader('Une place pour chaque article')
        combinations=category_combinations(frame)
        st.plotly_chart(charts.combinations_chart(combinations),theme=None,width='stretch',key='combinations_chart')
        st.caption('Chaque rectangle est une combinaison exacte des catégories étudiées. Ici, chaque article apparaît une seule fois : les surfaces totalisent 100 %.')
    common=int(frame['selected_categories'].map(lambda v: len(set(v))>1).sum())
    question('Pourquoi la somme des catégories dépasse-t-elle le total ?',
        f'{common:,} articles de cette sélection appartiennent à plusieurs catégories étudiées. La matrice compte ces recouvrements ; la carte par combinaison les rend exclusifs.', 'overlap_answer')


def use_query(term):
    st.session_state['query']=term
    st.session_state.pop('page',None)
    st.session_state.pop('detail',None)


def vocabulary(frame,filters):
    section_intro('LES MOTS DE LA SCIENCE', 'De quoi parle la recherche ?',
        'Explorez le vocabulaire des titres et confrontez deux expressions dans le temps.')
    if frame.empty:
        st.info('Aucun titre à explorer pour cette sélection.')
        return
    left,right=st.columns([1,1.25],gap='medium')
    with left,st.container(border=True):
        st.subheader('Les mots qui reviennent')
        count=st.slider('Nombre de mots',5,25,12,key='vocab_count')
        excluded=st.text_input('Mots à exclure',placeholder='ex. neural deep',key='excluded_terms')
        terms=title_vocabulary(frame,count,excluded)
        if terms.empty:
            st.info('Aucun mot exploitable après exclusion.')
        else:
            st.plotly_chart(charts.vocabulary_chart(terms),theme=None,width='stretch',key='vocabulary_chart')
            chosen=st.selectbox('Mot à explorer',terms['term'].tolist(),key='chosen_term')
            st.button('Utiliser ce mot comme filtre global',on_click=use_query,args=(chosen,),key='apply_term')
        st.caption('Présence par titre : un mot répété compte une seule fois. Séquences a–z de 4 lettres ou plus, quelques mots-outils exclus. Ce classement ne détecte ni sujets sémantiques ni citations.')
    with right,st.container(border=True):
        st.subheader('Un duel d’expressions')
        one=st.text_input('Expression A',value='transformer',key='term_a')
        two=st.text_input('Expression B',value='diffusion',key='term_b')
        normalized=st.toggle('Rapporter à 1 000 articles par année',value=True,key='terms_normalized')
        series={term:term_trajectory(frame,term,filters.year_min,filters.year_max,normalized=normalized)
                for term in dict.fromkeys([one.strip(),two.strip()]) if term}
        if series:
            st.plotly_chart(charts.terms_chart(series,normalized=normalized),theme=None,width='stretch',key='terms_chart')
        st.caption('Expressions littérales, sans distinction de casse, dans les titres uniquement. Le dénominateur est le total d’articles filtrés de l’année. Une année sans article a un taux non calculable.')
    question('Un mot plus fréquent désigne-t-il une recherche plus importante ?',
        'La fréquence décrit des titres, pas la qualité, les citations ou l’impact. Essayez les valeurs absolues puis les taux : une hausse du corpus peut expliquer une partie de la hausse du mot.', 'terms_answer')


def save_article(identifier):
    saved=list(st.session_state.get('reading_ids',[]))
    if identifier not in saved:
        saved.append(identifier)
    st.session_state['reading_ids']=saved


def clear_reading():
    st.session_state['reading_ids']=[]


def reading_list(articles,source):
    from ui.screens import results_table, article_detail
    section_intro('VOTRE SÉLECTION', 'Des graphiques aux lectures.',
        'Gardez les publications repérées pendant votre exploration et exportez votre sélection.')
    saved=st.session_state.get('reading_ids',[])
    selected=articles[articles['id'].isin(saved)]
    st.caption('Le panier est conservé pendant la session de ce navigateur et reste indépendant des filtres. Il disparaît à la fin de la session ; exportez-le pour le conserver.')
    if selected.empty:
        st.info('Votre panier est vide. Dans Exploration, ouvrez une fiche puis cliquez sur « Ajouter au panier de lecture ».')
        return
    st.metric('Articles dans le panier',len(selected))
    st.dataframe(results_table(selected,source),hide_index=True,width='stretch')
    by_id=selected.set_index('id')
    chosen=st.selectbox('Lire un article du panier',by_id.index.tolist(),format_func=lambda i:by_id.loc[i,'title'],key='reading_detail')
    article_detail(by_id.loc[chosen],source,location="reading")
    left,right=st.columns(2)
    left.download_button('Exporter le panier (CSV)',to_csv_bytes(selected),'arxiv_panier.csv','text/csv',key='reading_export')
    right.button('Vider le panier',on_click=clear_reading,key='clear_reading')


def workshop():
    section_intro('DÉMONSTRATEUR PÉDAGOGIQUE', 'Une question. Une exploration. Une preuve.',
        'Un parcours à projeter, puis à faire reproduire avec un autre jeu de données.')
    st.markdown('''
| Étape | Action dans l’application | Compétence à observer |
|---|---|---|
| 1 · Observer | Panorama → comparer les volumes annuels | Définir une unité et un périmètre |
| 2 · Comparer | Tendances → basculer en base 100 | Distinguer volume et progression relative |
| 3 · Questionner | Comparaison → Jaccard puis combinaisons | Comprendre le recouvrement et le dénominateur |
| 4 · Enquêter | Vocabulaire → transformer contre diffusion | Tester une hypothèse, normaliser un indicateur |
| 5 · Vérifier | Exploration → ouvrir une fiche et exporter | Relier un graphique à ses observations sources |
| 6 · Argumenter | Méthode → limites et provenance | Expliquer ce que les données ne permettent pas de conclure |
''')
    a,b,c=st.columns(3)
    with a,st.container(border=True):
        st.subheader('01 · Décrire')
        st.write('Choisissez une période. Trouvez un résultat et définissez précisément son unité.')
    with b,st.container(border=True):
        st.subheader('02 · Challenger')
        st.write('Changez le dénominateur, les catégories ou la période. Votre conclusion tient-elle encore ?')
    with c,st.container(border=True):
        st.subheader('03 · Prouver')
        st.write('Exportez les observations et vérifiez le calcul. Montrez un test et une PR relue.')
    st.info('Objectif : construire une application qui aide à raisonner. Le nombre de graphiques ne remplace pas la pertinence des questions, la qualité des calculs et la clarté des limites.')


def open_workspace(name):
    st.session_state['workspace']=name
    st.session_state['workspace_token']=st.session_state.get('workspace_token',0)+1


def overview_atlas(frame,filters):
    if frame.empty:
        return
    section_intro('CHANGEZ DE POINT DE VUE', 'Un corpus. Plusieurs histoires.',
        'Passez du calendrier aux communautés scientifiques, puis approfondissez dans les espaces d’exploration.')
    left,right=st.columns([1.35,1],gap='medium')
    with left,st.container(border=True):
        st.subheader('Le pouls des publications')
        table=monthly_counts(frame,filters.year_min,filters.year_max)
        st.plotly_chart(charts.heatmap(table),theme=None,width='stretch',key='overview_calendar')
        st.button('Explorer les tendances →',on_click=open_workspace,args=('Tendances',),key='open_trends')
    with right,st.container(border=True):
        st.subheader('La carte des communautés')
        st.plotly_chart(charts.combinations_chart(category_combinations(frame)),theme=None,width='stretch',key='overview_combinations')
        st.button('Explorer les recouvrements →',on_click=open_workspace,args=('Comparaison',),key='open_connections')
    st.caption('Calendrier : effectifs mensuels. Carte : combinaisons exactes des catégories étudiées, sans double comptage.')
