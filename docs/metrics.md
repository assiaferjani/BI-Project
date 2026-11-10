# Indicateurs pour les graphiques d'Ines

Les cinq fonctions de `src/metrics.py` reprennent les noms proposés dans la
[PR de conception #14](https://github.com/assiaferjani/BI-Project/pull/14).
Elles consomment la table **déjà filtrée** par l'interface et ne la modifient pas.
Elles acceptent les tableaux NumPy issus de Parquet et les tuples de `ui.data`.

| Fonction | Résultat |
| --- | --- |
| `unique_articles(df)` | Entier : identifiants distincts |
| `submissions_per_year(df)` | Colonnes `year`, `articles`, années croissantes |
| `articles_per_category(df)` | Colonnes `category`, `articles`, codes alphabétiques |
| `category_share(df)` | Colonnes `category`, `articles`, `share_pct` |
| `yearly_change(df)` | Colonnes `year`, `articles`, `change_pct` |

## Intégration proposée dans les écrans

Quand les branches de l'interface et des indicateurs seront réunies :

```python
from src.metrics import unique_articles, yearly_change, category_share

# filtered = apply_filters(articles, filters), calculé une seule fois dans app.py.
total = unique_articles(filtered)
trend = yearly_change(filtered, year_range=(filters.year_min, filters.year_max))
comparison = category_share(filtered)
```

Ces appels fournissent les données des cartes et graphiques ; cette contribution
ne modifie pas les écrans d'Ines.

## Années absentes, années à zéro et variation

Sans `year_range`, une année absente est inconnue : on ne l'ajoute pas, et on ne
calcule pas une variation qui sauterait une année. Par exemple, 2024 ne se compare
jamais à 2021 lorsque 2022 et 2023 sont absentes.

Si le fichier couvre exhaustivement la période choisie, passer
`year_range=(début, fin)` aux fonctions annuelles remplit les années sans résultat
avec zéro. Cela s'applique aussi à un résultat vide après recherche.
La période doit inclure tous les articles filtrés, sinon une erreur est levée.
Ne pas utiliser cette option pour transformer des données manquantes en zéros.

La variation est `100 * (N - N_précédent) / N_précédent`. Elle vaut `NaN`
(à afficher « non calculable ») si la base est absente ou nulle.
Passer de 100 à 120 donne +20 % ; passer de 1 à 0 donne −100 % ; passer
de 0 à 1 ne donne pas de pourcentage calculable. La première année affichée
n'utilise jamais des articles extérieurs aux filtres.

## Catégories et dénominateur

Un article dans cs.AI et cs.LG compte une fois dans le total et dans chaque catégorie.
Chaque part a pour dénominateur **le nombre d'articles uniques filtrés**, pas la somme
des appartenances. La somme des parts peut donc dépasser 100 %.

Le filtre des catégories sélectionne des articles. La comparaison décrit toutes
les `selected_categories` de ces articles : filtrer cs.AI peut donc aussi montrer
cs.LG si certains articles portent les deux catégories. Une comparaison limitée
aux seuls codes sélectionnés peut masquer les autres lignes après le calcul,
sans changer le dénominateur. Les catégories d'origine hors périmètre sont exclues.

Sans résultat, les tableaux sont vides avec leurs colonnes attendues, et le total
vaut zéro. Les fonctions reposent sur le contrat validé du pipeline : identifiants
non vides, une année cohérente par article, catégories structurées.

## Vérifier à la main sur la démonstration fictive

Trois articles uniques ; cs.AI = 2, cs.CL = 1, cs.LG = 1.
Les parts sont environ 66,67 %, 33,33 % et 33,33 %, soit 133,33 % au total.
Un article par année observée : 2020, 2021 et 2024. Avec la période 2020–2024,
la série est 1, 1, 0, 0, 1. Ces exemples ne sont pas des résultats scientifiques.
