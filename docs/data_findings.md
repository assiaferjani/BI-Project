# Première validation sur le vrai snapshot arXiv

> Mise à jour de l'interface : les graphiques sont désormais implémentés dans la
> branche `feat/arxiv-charts-delivery`. Leurs valeurs ont été vérifiées avec
> Streamlit AppTest sur le snapshot réel ; voir `reports/charts_validation.json`.
> La suite complète de cette branche compte 95 tests réussis. Les mentions de
> graphiques à construire ci-dessous décrivent le bilan initial.

Traitement effectué le 10 novembre 2026 sur le fichier contenu dans
`archive.zip`, téléchargé localement. Il s'agit de vrais articles et non du
petit jeu fictif utilisé pour les tests.

## Provenance et reproductibilité

- Source prévue du projet : [arXiv sur Kaggle](https://www.kaggle.com/datasets/Cornell-University/arxiv).
- Fichier : `arxiv-metadata-oai-snapshot.json`, 5 667 572 509 octets décompressés.
- Empreinte SHA-256 du snapshot :
  `97a7fee00eac38ee5ea92d5cddae351cf3cbb444775a397ac60efb773f217b10`.
- Version Kaggle : **non renseignée**. Le nom du ZIP ne permet pas de la déduire.
  Le traitement est identifié par l'empreinte du fichier, sans prétendre connaître
  le numéro de version ou garantir que le téléchargement courant sera identique.
- Code de préparation : commit `9d5f67d` ; Python 3.11.18, PyArrow 26.0.1.
- Périmètre : premier dépôt v1 de 2020 à 2024 inclus ; au moins une catégorie
  parmi cs.AI, cs.LG et cs.CL. Toutes les lignes du snapshot ont été parcourues.

Le [manifeste](../reports/dataset_manifest.json) conserve les tailles et empreintes
des fichiers source et préparé. Les données brutes et le Parquet restent dans
`data/raw/` et `data/processed/`, ignorés par Git. Seuls les petits bilans sont publiés.

## Bilan du traitement

| Résultat | Nombre de lignes |
| --- | ---: |
| Lignes du snapshot lues | 3 233 620 |
| Hors période 2020–2024 | 2 234 846 |
| Dans la période mais hors catégories choisies | 769 154 |
| Articles uniques retenus | **229 620** |
| JSON, identifiants ou dates v1 invalides détectés | 0 |
| Doublons parmi les lignes admissibles | 0 |

Les trois postes « hors période », « hors catégories » et « retenus » totalisent
exactement le nombre de lignes lues. Les motifs sont comptés successivement,
pas indépendamment : les catégories des articles déjà exclus pour leur année
ne sont pas évaluées. Les doublons annoncés concernent le périmètre admissible.

Dans le Parquet, les 229 620 identifiants sont uniques et non vides. Les dates
vont du 01/01/2020 au 31/12/2024 et concordent avec les années. Aucun titre,
résumé ou champ auteurs vide n'a été observé. Les listes de catégories sont
valides, et chaque catégorie sélectionnée appartient aux catégories originales.
Ces contrôles structurels ne prouvent pas l'exactitude scientifique des textes.

Le traitement complet a pris environ 46 secondes, avec un pic de mémoire
d'environ 243 Mio sur ce poste lors de cet essai. Ce sont des mesures d'une
exécution, pas une garantie sur d'autres machines.

## Premiers indicateurs observés

| Année du premier dépôt | Articles uniques | Variation annuelle |
| --- | ---: | ---: |
| 2020 | 33 566 | Non calculable dans la période |
| 2021 | 37 160 | +10,71 % |
| 2022 | 40 536 | +9,09 % |
| 2023 | 51 037 | +25,91 % |
| 2024 | 67 321 | +31,91 % |

Les volumes de dépôts augmentent sur chaque année de ce périmètre. La hausse
annuelle la plus élevée observée ici est celle de 2024. Ces résultats décrivent
les dépôts du sous-ensemble ; ils ne mesurent ni qualité, ni impact, ni citations.

| Catégorie | Articles portant le code | Part des articles uniques |
| --- | ---: | ---: |
| cs.AI | 89 660 | 39,05 % |
| cs.CL | 58 471 | 25,46 % |
| cs.LG | 153 967 | 67,05 % |

65 207 articles portent plusieurs des catégories retenues. Les 302 098
appartenances ne représentent donc pas 302 098 articles différents. Les parts
totalisent environ 131,56 % parce que les catégories se recouvrent.

Les chiffres non arrondis sont conservés dans [arxiv_profile.json](../reports/arxiv_profile.json).
Les règles de calcul se trouvent dans [metrics.md](metrics.md).

## Vérification de l'interface publiée par Ines

Vérification sur une copie temporaire de sa branche de recherche/export au commit
`31f3743`, réunie avec les indicateurs et le nouveau contrôle de qualité :

- 88 tests réussis sur l'ensemble ; 71 sur la branche de cette contribution seule.
- L'application charge les 229 620 vrais articles et n'affiche pas le bandeau fictif.
- Le filtre cs.CL seul affiche 58 471 articles.
- Années 2023–2024 + cs.CL + recherche « transformer » : 3 260 articles uniques,
  exactement 3 260 lignes dans l'export CSV.
- La page 2 et une recherche sans résultat fonctionnent sans exception.

Les interactions ont été exécutées avec l'outil de test Streamlit, et le CSV a
été relu avec pandas. Ce contrôle ne remplace pas une revue visuelle du navigateur
ou une ouverture du CSV dans un tableur par le binôme.
Le [relevé de cet essai](../reports/real_ui_smoke.json) identifie le cas et les résultats.

## Reproduire le bilan

```bash
python -m src.profile_data \
  --input data/processed/articles.parquet \
  --output reports/arxiv_profile.json
python -m pytest -q
```

Pour reproduire l'extraction, utiliser la commande du README et le même snapshot
(empreinte ci-dessus). Le libellé utilisé lors de cet essai était
`--source-version kaggle-version-not-recorded`, faute de numéro connu.
Consigner ce numéro dès qu'il est retrouvé, sans inventer sa valeur.

## Suite du travail

La préparation et les calculs de la partie A ont désormais une validation sur
le vrai fichier. Ines peut brancher les graphiques sur `src.metrics`. Le binôme
doit encore relire les contributions, finaliser leur intégration dans `main`,
reproduire le lancement sur le poste d'Ines et préparer la présentation.
