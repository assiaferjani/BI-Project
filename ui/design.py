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
      <div class="hero-copy"><div class="eyebrow hero-eyebrow">LES IDÉES LAISSENT DES TRACES.</div>
      <h1>Explorez la recherche.<br><em>Repérez les tendances.</em></h1>
      <p>Une autre perspective sur les publications en intelligence artificielle.<br>
      Comparez les domaines, suivez leur évolution et trouvez votre prochain article.</p>
      <div class="hero-tags"><span>{amount} articles</span><span>{first_year}—{last_year}</span>
      <span>cs.AI · cs.LG · cs.CL</span></div></div>
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
