# BI-Project — arXiv Explorer

Projet BI d'Assia Ferjani (personne A) et Ines Makhlouf (personne B).

**Question proposée :** comment évoluent les dépôts d'articles dans les catégories
`cs.AI`, `cs.LG` et `cs.CL` entre 2020 et 2024, et comment retrouver les articles
correspondant à un sujet ? Ce périmètre reste à valider ensemble.

Le dataset choisi est [arXiv sur Kaggle](https://www.kaggle.com/datasets/Cornell-University/arxiv).
Le projet contient la préparation, les indicateurs et une première interface.
Le snapshot réel a été traité : **229 620 articles** retenus sur 2020–2024.
Consulter le [bilan vérifié](docs/data_findings.md) pour la provenance, les chiffres
et les limites. Recherche, fiches, pagination et export sont intégrés à cette
branche. Les graphiques et la livraison dans `main` restent à finaliser.
La [checklist de revue](docs/review_checklist.md) décrit les vérifications
à reproduire par Ines.

## Répartition

| Personne | Réalisation | Revue |
| --- | --- | --- |
| Assia — A | Préparation des données, qualité, calculs et tests | PR d'Ines |
| Ines — B | Interface, graphiques, recherche, export et guide utilisateur | PR d'Assia |

Chaque personne travaille sur une branche par tâche. Une PR est relue par l'autre
avant fusion vers `main`. Voir [le guide de collaboration](CONTRIBUTING.md).

## Installer — Python 3.11 ou 3.12

Depuis la racine du dépôt, sur Linux / macOS :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Sous Windows PowerShell : `py -m venv .venv`, puis
`.venv\Scripts\Activate.ps1` et la même commande d'installation.

## Essayer sans télécharger Kaggle

Le fichier de démonstration est **fictif** : il sert à vérifier le fonctionnement,
pas à produire des conclusions scientifiques. Il contient 6 lignes, dont
3 articles retenus, 1 doublon, 1 article hors période et 1 hors catégories.

```bash
python -m src.prepare_data \
  --input data/sample/arxiv_demo.jsonl \
  --output data/processed/demo.parquet \
  --source-version synthetic-demo-v1
python -m pytest
```

Résultats : `data/processed/demo.parquet` et
`data/processed/demo.quality.json`. Les sorties sont ignorées par Git.
Les compteurs de qualité sont aussi affichés dans le terminal.

## Préparer les vraies données

1. Depuis la page Kaggle, télécharger et décompresser
   `arxiv-metadata-oai-snapshot.json`. Les PDF des articles ne sont pas nécessaires.
2. Placer ce fichier dans `data/raw/` (créer le dossier si nécessaire).
3. Noter la version exacte du dataset dans Kaggle et la date du téléchargement.
4. Remplacer `VERSION_KAGGLE` ci-dessous par cette version, puis lancer :

```bash
python -m src.prepare_data \
  --input data/raw/arxiv-metadata-oai-snapshot.json \
  --output data/processed/articles.parquet \
  --source-version VERSION_KAGGLE \
  --start-year 2020 --end-year 2024 \
  --categories cs.AI cs.LG cs.CL
```

Le programme lit le fichier entier progressivement et produit un Parquet et un
rapport JSON : empreinte SHA-256 de la source, paramètres, versions logicielles,
date d'exécution et compteurs de qualité. La mémoire contient un bloc d'articles
et les identifiants déjà retenus ; elle ne contient pas le snapshot complet.
Le premier traitement réel et son empreinte source sont documentés dans
[docs/data_findings.md](docs/data_findings.md). Le numéro de version Kaggle de
ce téléchargement n'a pas été renseigné ; il ne peut pas être déduit du nom du ZIP.

Pour vérifier le Parquet et recalculer le bilan :

```bash
python -m src.profile_data \
  --input data/processed/articles.parquet \
  --output reports/arxiv_profile.json
```

## Contrat pour l'interface d'Ines

```python
import pandas as pd

articles = pd.read_parquet("data/processed/articles.parquet")
total = articles["id"].nunique()
```

`categories` et `selected_categories` sont des colonnes de listes en Parquet ;
pandas peut les restituer comme des tableaux NumPy. Ne pas les traiter comme des
chaînes séparées par des virgules. Utiliser `explode` pour compter par catégorie.
Tous les indicateurs devront utiliser le même ensemble filtré d'articles.

La date de référence est celle de **v1**, jamais `update_date`. Un article portant
deux catégories compte une fois au total, mais dans chacune des deux catégories.

## Structure et prochaines contributions

```text
src/prepare_data.py       préparation JSONL → Parquet + rapport qualité
src/profile_data.py       contrôle du contrat et bilan du Parquet
src/metrics.py            calculs des indicateurs BI
reports/                 petits bilans vérifiés, sans les articles
data/sample/             données fictives de démonstration
app.py                   point d'entrée de l'application Streamlit
ui/                      chargement, filtres et écrans de l'interface
tests/                   cas contrôlés pour le traitement et l'interface
docs/data_dictionary.md   colonnes préparées et règles pour l'interface
docs/methodology.md       périmètre, règles, limites et provenance
docs/next_steps.md        tâches d'Assia et d'Ines après cette PR
```

## Lancer l'application

Après la préparation des données (vraies ou de démonstration) :

```bash
python -m streamlit run app.py
```

L'application charge `data/processed/articles.parquet` s'il existe, sinon
`data/processed/demo.parquet` en affichant un bandeau « données fictives ».
Sans aucun des deux, elle indique la commande à lancer.

Les résultats réels documentés concernent uniquement le snapshot et le périmètre
du [bilan de validation](docs/data_findings.md), pas l'ensemble de la recherche.
