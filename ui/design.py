"""Identité visuelle de l'application, sans dépendance à des polices externes."""

from pathlib import Path

import streamlit as st


def apply_design():
    css = Path(__file__).with_name("theme.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def sidebar_brand():
    st.sidebar.markdown('''
    <div class="sidebar-brand"><span class="brand-symbol">a<span>∕</span></span>
    <div>arXiv<span class="brand-sub">EXPLORER</span></div></div>
    <div class="sidebar-intro">Votre prochaine découverte<br>commence ici.</div>
    <div class="sidebar-rule"></div>
    <div class="eyebrow sidebar-eyebrow">VOTRE PÉRIMÈTRE</div>
    ''', unsafe_allow_html=True)


def hero(count: int, first_year: int, last_year: int, *, is_demo: bool):
    amount = f"{count:,}".replace(",", " ")
    mode = "Démonstration fictive" if is_demo else "Métadonnées arXiv"
    st.markdown(f'''
    <div class="topbar"><span class="breadcrumb">OBSERVATOIRE DE LA RECHERCHE
    <span class="breadcrumb-slash">/</span> INTELLIGENCE ARTIFICIELLE</span>
    <span class="source-badge"><i></i>{mode}</span></div>
    <section class="research-hero">
      <div class="hero-copy"><div class="eyebrow hero-eyebrow">RESEARCH LAB · APPRENDRE PAR L’EXPLORATION.</div>
      <h1>Explorez la recherche.<br><em>Repérez les tendances.</em></h1>
      <p>Un laboratoire interactif pour lire, comparer et questionner la recherche.<br>
      Comparez les domaines, testez vos hypothèses et composez votre parcours de lecture.</p>
      <div class="hero-tags"><span>{amount} articles</span><span>{first_year}—{last_year}</span>
      <span>10 visualisations · 8 espaces</span></div></div>
      <div class="orbit-art" aria-hidden="true"><div class="orbit orbit-one"></div>
      <div class="orbit orbit-two"></div><div class="orbit orbit-three"></div>
      <div class="orbit-core">a<span>∕</span></div><i class="orbit-point"></i>
      <span class="orbit-label">CONNECTER LES IDÉES</span></div>
    </section>
    ''', unsafe_allow_html=True)


def section_intro(kicker: str, title: str, description: str):
    # Textes constants de l'interface uniquement, pas de contenu des articles.
    st.markdown(f'<div class="section-intro"><div class="eyebrow">{kicker}</div>'
                f'<h2>{title}</h2><p>{description}</p></div>', unsafe_allow_html=True)
