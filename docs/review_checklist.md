# Revue d'Ines avant intégration finale

Les PR #13 (recherche/export) et #14 (conception) sont fusionnées dans
`feat/arxiv-data-foundation`. La PR #16 ajoute les contrôles des données réelles
et inclut cette branche commune. Elle est à relire par Ines. La PR #10 porte
la branche commune vers `main` ; les graphiques restent une contribution distincte.

## Vérifier depuis une nouvelle copie

```bash
git clone --branch feat/arxiv-real-data-validation \
  https://github.com/assiaferjani/BI-Project.git arxiv-review
cd arxiv-review
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.prepare_data \
  --input data/sample/arxiv_demo.jsonl \
  --output data/processed/demo.parquet \
  --source-version synthetic-demo-v1
python -m pytest -q
python -m streamlit run app.py
```

Résultats attendus : 3 articles fictifs retenus, 90 tests réussis, application
avec un avertissement de démonstration. La recherche, la sélection de catégories
et la fiche d'article doivent fonctionner. Les liens des articles fictifs sont
masqués. Ces données ne servent pas à interpréter les tendances scientifiques.

## Vérifier les données réelles

Utiliser le snapshot décrit dans `reports/dataset_manifest.json`, puis la
commande de préparation du README. Si l'empreinte source diffère, comparer les
versions avant de conclure à un défaut de calcul. Le numéro Kaggle de notre
snapshot reste à retrouver.

```bash
python -m src.profile_data \
  --input data/processed/articles.parquet \
  --output reports/local_review_profile.json
```

Le rapport local est une sortie de revue : il ne faut pas l'ajouter à la PR.

| Cas | Résultat attendu pour le snapshot documenté |
| --- | ---: |
| Toutes les années et catégories | 229 620 articles uniques |
| cs.CL, toutes les années | 58 471 articles |
| cs.CL, 2023–2024, recherche `transformer` | 3 260 articles |
| Export du cas précédent | 3 260 lignes hors en-tête |
| Recherche `[aucun article improbable zzzz]` | 0 article, message explicite |

## Revue dans GitHub

Lire les changements de la PR #16 : date v1, unicité, cohérence des années,
catégories qui se recouvrent, tests et bilans. Reproduire les commandes avant
d'approuver, puis mentionner les résultats réellement observés dans la revue.
Une exécution automatique par Codex ne remplace pas cette revue du binôme.

Après approbation et fusion de #16 dans la branche commune, relire le diff final
de #10 vers `main`, qui inclura toutes les contributions intégrées. Si #10 est
fusionnée en premier, vérifier le diff et retargeter #16 vers `main`.

## Ce qui reste pour la livraison

- Graphiques utilisant `src.metrics` sur la même table filtrée que l'export.
- Vérification visuelle sur les deux postes et ouverture du CSV dans un tableur.
- Version Kaggle si elle est retrouvée, captures et démonstration commune.
- Installation depuis un nouveau clone avec un environnement neuf.
