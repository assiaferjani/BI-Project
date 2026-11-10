# Conception de l'interface : arXiv Explorer

Document du membre B (interface). Il décrit les écrans et les décisions
d'interface. Les données, le périmètre et les colonnes sont définis par
`docs/data_dictionary.md` et `docs/methodology.md` : ce document ne les
redéfinit pas.

## Public et usage

Étudiants et personnes qui commencent une veille scientifique. Ils veulent
comparer des volumes de dépôts, explorer une période et retrouver des articles
à lire, sans écrire de code.

## Écrans

Une seule page, des filtres communs dans la barre latérale, quatre onglets.

```
+--------------------+-----------------------------------------------------+
| FILTRES            |  arXiv Explorer                                     |
|                    |  [ Vue d'ensemble | Comparaison | Exploration | Méthode ]
| Années de dépôt    |                                                     |
| [2020 ======2024]  |  Articles uniques   Période      Catégories         |
|                    |  [    12 345    ]  [2020-2024]   [    3    ]         |
| Catégories         |                                                     |
| [cs.AI] [cs.LG]... |  Dépôts par année (courbe)                          |
|                    |                                                     |
| Recherche          |                                                     |
| [______________]   |                                                     |
+--------------------+-----------------------------------------------------+
```

| Écran | Contenu |
| --- | --- |
| Vue d'ensemble | Articles uniques, période filtrée, catégories étudiées, dépôts par année et variation annuelle. |
| Comparaison | Volumes et parts par catégorie, avec la définition du comptage sous le graphique. |
| Exploration | Recherche dans les titres et les résumés, liste paginée, fiche d'un article, export CSV. |
| Méthode | Source, période, périmètre, règles de calcul et limites. |

## Décisions d'interface

1. **Une seule table filtrée.** Les filtres sont appliqués une fois ; cartes,
   graphiques, liste et export partent tous de cette table.
2. **Plusieurs catégories sélectionnées :** un article est retenu si au moins
   une de ses catégories est sélectionnée.
3. **Aucune catégorie sélectionnée** signifie « toutes ».
4. **Recherche :** expression littérale (pas d'expression régulière), sans tenir
   compte des majuscules, cherchée dans le titre et le résumé.
5. **Résultat vide :** total à zéro, liste vide et message explicite, sans erreur.
6. **Double comptage :** tout graphique par catégorie porte la mention « un
   article peut porter plusieurs catégories ; la somme dépasse le total ».
7. **Données fictives :** quand l'application charge la démonstration, un
   bandeau l'annonce et les liens arXiv sont masqués, car ces articles
   n'existent pas.
8. **Fichier absent :** l'application affiche la commande à lancer au lieu
   d'une erreur technique.

## Colonnes utilisées par l'interface

Toutes les colonnes de `docs/data_dictionary.md` sont utilisées et suffisent
pour les quatre écrans : `id`, `title`, `abstract`, `authors`, `submitted_at`,
`year`, `categories`, `selected_categories`, `arxiv_url`. Aucune colonne
supplémentaire n'est demandée.

## Fonctions de calcul attendues

Pour les graphiques, l'interface appellera des fonctions de `src/metrics.py`
sur la table déjà filtrée. Noms proposés, à ajuster par A :

| Fonction | Retour |
| --- | --- |
| `unique_articles(df)` | entier : nombre de `id` distincts |
| `submissions_per_year(df)` | table `year`, `articles` |
| `articles_per_category(df)` | table `category`, `articles` (un article compte dans chacune de ses catégories étudiées) |
| `category_share(df)` | table `category`, `articles`, `share_pct` = 100 × articles de la catégorie / articles uniques |
| `yearly_change(df)` | table `year`, `articles`, `change_pct` ; valeur absente si l'année précédente vaut 0 ou manque |
