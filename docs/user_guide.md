# Utiliser arXiv Explorer

## Démarrer

Suivre l'installation du README, préparer le fichier de démonstration ou le vrai
snapshot, puis exécuter `python -m streamlit run app.py` depuis la racine du dépôt.
Ouvrir l'adresse locale indiquée par Streamlit. Arrêter le serveur avec Ctrl+C.

Le bandeau de démonstration indique que les articles sont fictifs. Pour une
analyse scientifique, préparer `data/processed/articles.parquet` avec le vrai
snapshot. Ce fichier est choisi en priorité ; le fichier fictif sert de solution
de repli lorsqu'il n'est pas présent.

## Choisir les articles

La barre latérale propose une période inclusive, plusieurs catégories et une
recherche dans les titres et résumés. Toutes les vues utilisent ces mêmes filtres.

Sans catégorie sélectionnée, toutes les catégories étudiées sont retenues.
Avec plusieurs catégories, un article est retenu s'il en possède au moins une.
La recherche ignore les majuscules et cherche une expression littérale : saisir
`language models` cherche cette expression, sans effectuer une recherche sémantique.
Vider le champ pour supprimer la recherche. Les espaces superflus sont ignorés.

## Lire les graphiques

- **Vue d'ensemble** : articles uniques, période, catégories présentes, courbe
  annuelle et variation par rapport à l'année civile précédente. Survoler un point
  pour lire sa valeur. Le tableau dépliable permet de vérifier les chiffres.
- **Variation** : la première année affichée et une base précédente nulle donnent
  « Non calculable ». Les années couvertes sans résultat valent zéro. Une période
  d'une seule année ne permet pas de calculer une variation dans la sélection.
- **Comparaison** : nombre d'articles portant chaque catégorie et part du total
  filtré. Un article cs.AI + cs.LG contribue aux deux catégories et une seule
  fois au total. La somme des parts peut donc dépasser 100 %.

Le filtre choisit des articles ; la comparaison montre toutes leurs catégories
étudiées. Un article retenu par cs.AI peut également contribuer à cs.LG.
La part de chaque catégorie est divisée par le total des articles retenus.

## Explorer et exporter

L'onglet Exploration liste les articles du plus récent au plus ancien, par pages
de 25. Choisir une page, puis un article pour afficher son résumé et son lien.
Les liens sont masqués pour les articles fictifs.

Le bouton CSV exporte **tous les résultats filtrés**, et non seulement la page
visible. Le fichier comprend identifiant, titre, auteurs, date, année, catégories,
résumé et lien. Il est encodé en UTF-8 avec BOM ; les listes de catégories sont
séparées par ` ; `. Dans un tableur, choisir la virgule comme séparateur de colonnes
si la détection automatique ne convient pas.

Si aucun article ne correspond, élargir la période, enlever une catégorie ou
effacer la recherche. Les anciennes valeurs des graphiques ne restent pas affichées.

## Dépannage

- **Aucun fichier trouvé** : exécuter la préparation du README, puis relancer.
- **Module introuvable** : activer `.venv` et installer `requirements.txt`.
- **Chiffres différents** : vérifier les filtres, le mode réel/fictif et l'empreinte
  du snapshot. La version téléchargée aujourd'hui peut différer de celle étudiée.
- **Catégories supérieures au total** : c'est le recouvrement des catégories,
  expliqué dans l'onglet Méthode.

## Interpréter avec prudence

Les indicateurs décrivent les dépôts arXiv du sous-ensemble, datés par la version
v1. Ils ne mesurent ni la qualité des articles, ni les citations, ni l'ensemble
de la recherche mondiale. Consulter l'onglet Méthode et `docs/data_findings.md`.

## Espaces du démonstrateur pédagogique

La version enrichie propose huit espaces. **Tendances** ajoute un calendrier
mensuel, la base 100 et les effectifs agrégés par mois. **Comparaison** ajoute une
matrice des intersections (option Jaccard) et une carte des combinaisons exclusives.
**Vocabulaire** permet de régler le nombre de mots, d'en exclure et de comparer
deux expressions dans les titres. Le bouton d'exploration d'un mot modifie la
recherche globale dans la barre latérale.

Dans **Exploration**, tirer un article au hasard ou choisir une fiche, puis
l'ajouter au **Panier de lecture**. Celui-ci conserve sa sélection malgré les
changements de filtres, pendant la session du navigateur. Il est exportable et
peut être vidé. **Atelier** présente un parcours de questions et de compétences.

Les scénarios de la barre latérale initialisent un panorama ou une enquête
`transformer`. Le mode projection agrandit les explications et réduit le bandeau.
Les questions à révéler, sous les graphiques, utilisent les filtres courants.
Voir `docs/teacher_demo.md` pour une séance complète et les règles des nouveaux
indicateurs.
