# Conception : Spotify Explorer

Document de travail du membre B (application et visualisation). Il fixe la
question, le public, les écrans et les décisions d'interface. Tout ce qui
touche au périmètre et aux données est une **proposition à valider avec A**
avant le développement du pipeline.

## Question

> Comment les caractéristiques audio des titres Spotify (énergie, acoustique,
> dansabilité, durée) évoluent-elles entre 1960 et 2020 dans six grandes
> familles de genres, et comment retrouver les titres qui correspondent à une
> période et à un genre ?

**Public :** étudiants et curieux de musique qui veulent comparer des époques
et des genres sans écrire de code.

**Utilité :** comparer des volumes et des profils audio, explorer une période,
retrouver des titres à écouter.

## Source

Kaggle, « Spotify Dataset 1921-2020, 600k+ Tracks » (yamaerenay). Deux fichiers
sont utilisés : `tracks.csv` (un titre par ligne) et `artists.csv` (genres des
artistes). `dict_artists.json` (artistes similaires) n'est pas utilisé.

## Périmètre proposé

| Règle | Proposition | Raison |
|---|---|---|
| Période | année de sortie entre 1960 et 2020 inclus | 2021 est incomplète (dernière date : 2021-04-16) ; une ligne isolée est datée 1900 |
| Genres | titres dont au moins un artiste porte un genre d'une des six familles : pop, rock, hip hop, jazz, classical, electronic | les genres ne sont pas dans `tracks.csv` : ils viennent des artistes |
| Unicité | un titre = un `id`, compté une seule fois | un titre peut appartenir à plusieurs familles |

Mesures préliminaires faites par B sur les fichiers téléchargés le 2026-11-10
(à recalculer et confirmer par le pipeline de A) :

- `tracks.csv` : 586 672 lignes, aucun `id` en double, 71 titres sans nom ;
- 506 331 titres dans la période 1960-2020 ;
- 333 928 d'entre eux ont au moins une famille de genres avec la règle proposée ;
- 102 702 titres appartiennent à plusieurs familles : la somme des comptes par
  famille dépasse donc le total de titres uniques ;
- `release_date` a trois précisions : jour (448 081 lignes), année seule
  (136 489) et année-mois (2 102). L'année est toujours disponible.

## Écrans

L'application tient sur une page, avec des filtres communs dans la barre
latérale et quatre onglets.

```
+------------------+------------------------------------------------------+
| FILTRES          |  Spotify Explorer                                    |
|                  |  [ Vue d'ensemble | Comparaison | Exploration | Méthode ]
| Années           |                                                      |
| [1960 ====2020]  |  Titres uniques   Période     Familles   Popularité  |
|                  |  [   12 345   ]  [1960-2020]  [  6  ]    [  31  ]    |
| Familles         |                                                      |
| [pop] [rock] ... |  Titres par année de sortie                          |
|                  |  (courbe)                                            |
| Recherche        |                                                      |
| [____________]   |                                                      |
+------------------+------------------------------------------------------+
```

| Écran | Contenu |
|---|---|
| Vue d'ensemble | Nombre de titres uniques, période couverte, familles étudiées, évolution annuelle du nombre de titres et des caractéristiques audio moyennes. |
| Comparaison | Volumes et profil audio moyen par famille, avec la définition du comptage affichée sous le graphique. |
| Exploration | Recherche dans les titres et les artistes, filtres année et famille, liste paginée, fiche d'un titre, export CSV. |
| Méthode | Source, période, périmètre, règles de calcul et limites. |

## Décisions d'interface

1. **Une seule table filtrée.** Les filtres sont appliqués une fois ; les
   cartes, les graphiques, la liste et l'export partent tous de cette table.
2. **Plusieurs familles sélectionnées :** un titre est retenu si au moins une
   de ses familles est sélectionnée.
3. **Aucune famille sélectionnée** signifie « toutes ». La même convention
   s'applique partout.
4. **Recherche :** le texte saisi est une expression littérale (pas une
   expression régulière), sans tenir compte de la casse ni des accents,
   cherchée dans le titre et dans les noms d'artistes.
5. **Résultat vide :** total à zéro, liste vide et message explicite, sans
   erreur.
6. **Double comptage :** tout graphique par famille affiche la mention « un
   titre peut appartenir à plusieurs familles ; la somme dépasse le total ».
7. **Données de démonstration :** tant que le fichier préparé n'existe pas,
   l'application charge un petit échantillon et l'indique par un bandeau
   visible.

## Limites à afficher

- La popularité est celle mesurée par Spotify au moment de la collecte, pas au
  moment de la sortie du titre.
- Plus de titres dans une famille ne signifie pas une meilleure musique ni plus
  d'écoutes.
- Les genres sont ceux des artistes, pas ceux des titres.
- Le jeu de données n'est pas un échantillon représentatif du catalogue
  Spotify ; sa méthode de collecte n'est pas documentée en détail.
