# Contrat de données pour l'interface

Une ligne du Parquet représente un article unique admissible au périmètre.
Les noms ci-dessous sont le contrat proposé entre la préparation d'Assia et
l'interface d'Ines. Toute modification devra être discutée dans une PR.

| Colonne | Type Parquet | Règle |
| --- | --- | --- |
| `id` | string | Texte conservé, espaces extérieurs retirés ; unique et non vide |
| `title` | string | Espaces normalisés ; vide si absent ou non textuel |
| `abstract` | string | Même nettoyage ; aucun résumé inventé |
| `authors` | string | Texte d'origine avec espaces normalisés ; ne pas compter les auteurs en séparant les virgules |
| `submitted_at` | date32 | Date UTC de la version explicitement nommée `v1` |
| `year` | int16 | Année dérivée de `submitted_at` |
| `categories` | list&lt;string&gt; | Tous les codes d'origine, sans doublons, dans leur ordre d'origine |
| `selected_categories` | list&lt;string&gt; | Intersection avec les catégories du traitement |
| `arxiv_url` | string | `https://arxiv.org/abs/` suivi de l'identifiant échappé |

Les identifiants fictifs de la démonstration ne donnent pas de vrais liens arXiv.
Dans pandas, une cellule de liste Parquet peut être un tableau NumPy.

## Calculs à implémenter dans une prochaine PR

- Total : nombre de `id` distincts après filtres.
- Dépôts par année : nombre de `id` distincts groupés par `year`.
- Catégorie : éclater `selected_categories`, puis compter les `id` distincts par code.
- Variation : `(N - N_précédent) / N_précédent * 100` ; résultat indisponible
  si la période précédente manque ou si le dénominateur vaut zéro.

Plusieurs catégories sélectionnées signifient « au moins l'une d'elles ».
Le total des comptes par catégorie peut dépasser le nombre d'articles uniques.
`update_date` et l'ordre de la liste `versions` ne déterminent pas l'année.
