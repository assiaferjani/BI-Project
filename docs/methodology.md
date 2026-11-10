# Méthode, provenance et limites

## Source

Métadonnées du [dataset arXiv publié sur Kaggle](https://www.kaggle.com/datasets/Cornell-University/arxiv).
La fiche annonce CC0 pour les métadonnées ; les licences des articles sont
distinctes. Vérifier la fiche de la version effectivement récupérée.
Le snapshot réel n'a pas encore été téléchargé ni analysé pour cette contribution.

Au téléchargement, noter ici ou dans une prochaine PR la version Kaggle,
la date de récupération et les conditions de la source. `--source-version`
est obligatoire en ligne de commande. La version saisie est déclarative :
le programme ne la vérifie pas auprès de Kaggle.

## Règles du traitement

1. Lire un objet JSON par ligne du fichier décompressé ; calculer simultanément
   l'empreinte SHA-256 sur tous les octets du fichier.
2. Refuser les lignes mal formées, les objets non dictionnaires et les identifiants
   absents ou non textuels.
3. Chercher `v1` par son nom, même si `v2` arrive en premier. Parser le format de date
   RFC utilisé par le snapshot. Convertir en UTC ; une date sans fuseau est traitée
   comme UTC. Une date invalide ou une version absente entraîne une exclusion.
4. Garder les années 2020 à 2024 incluses et les articles portant au moins un code
   parmi `cs.AI`, `cs.LG`, `cs.CL`. Ces paramètres sont modifiables en CLI.
5. Parmi les lignes admissibles, garder la première occurrence de chaque `id`.
   Cette règle est déterministe pour un snapshot et un ordre de lignes identiques.
6. Normaliser les espaces des titres, résumés et auteurs. Conserver les textes
   manquants comme chaînes vides, et compter ces absences parmi les articles retenus.
7. Écrire le Parquet par blocs. Les identifiants retenus restent en mémoire pour
   dédupliquer ; la consommation mémoire augmente donc avec leur nombre.

Chaque ligne reçoit **un seul** résultat dans `outcomes`, selon cet ordre de règles.
La somme de ces résultats égale `lines_read`. Ce ne sont pas des mesures indépendantes
de tous les défauts : une ligne rejetée pour sa date n'est plus examinée pour ses catégories.
`duplicate_retained_id` ne mesure que les doublons dans les lignes admissibles.

Le rapport contient les paramètres, l'empreinte et le nom du fichier source,
les versions Python/PyArrow et les compteurs. Conserver aussi le commit du code
utilisé. L'horodatage d'exécution varie à chaque lancement, même si les données
préparées sont identiques. Une sortie vide reste un Parquet lisible et typé.
Une nouvelle exécution remplace les sorties après la réussite du traitement.

## Interprétation

Le sous-ensemble est exhaustif pour les filtres appliqués au snapshot choisi,
pas pour toute la recherche mondiale. Plus de dépôts ne signifie pas meilleure
qualité scientifique. Les catégories se recouvrent. Aucun classement par
citations n'est calculable avec les colonnes retenues.

Les premières lignes d'un snapshot ne constituent pas un échantillon représentatif.
Le fichier fictif du dépôt sert uniquement au développement et aux tests.

## Références techniques

- [PyArrow ParquetWriter](https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html)
- [Python email.utils](https://docs.python.org/3/library/email.utils.html)

La première version a été préparée avec une aide IA. Les tests couvrent des cas
contrôlés ; ils ne remplacent pas la validation sur le snapshot réel.
