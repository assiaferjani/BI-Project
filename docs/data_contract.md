# Contrat de données entre le pipeline (A) et l'application (B)

Proposition de B, à valider par A. Une fois accepté, ce contrat ne change que
par une PR relue par les deux membres.

## Fichier préparé

- Chemin : `data/processed/tracks.parquet` (généré, ignoré par Git).
- Une ligne par titre ; `id` unique.
- Échantillon de démonstration au même format :
  `data/sample/tracks_sample.parquet` (versionné, quelques centaines de lignes).

| Colonne | Type | Règle |
|---|---|---|
| `id` | texte | Identifiant Spotify du titre, unique et non vide. |
| `name` | texte | Titre, espaces nettoyés. Valeur absente : chaîne vide ; l'interface affiche « (sans titre) ». |
| `artists` | liste de textes | Noms des artistes, dans l'ordre d'origine. |
| `artist_ids` | liste de textes | Identifiants Spotify des artistes. |
| `release_date` | texte | Valeur d'origine, non modifiée (`AAAA`, `AAAA-MM` ou `AAAA-MM-JJ`). |
| `release_precision` | texte | `year`, `month` ou `day`, selon la forme de `release_date`. |
| `year` | entier | Année de sortie, tirée de `release_date`. |
| `genres` | liste de textes | Tous les genres des artistes du titre, sans doublon. |
| `selected_genres` | liste de textes | Familles du périmètre auxquelles le titre appartient ; jamais vide dans le fichier préparé. |
| `popularity` | entier 0-100 | Valeur d'origine. |
| `duration_ms` | entier | Durée en millisecondes. |
| `explicit` | booléen | Valeur d'origine convertie. |
| `danceability`, `energy`, `valence`, `acousticness`, `instrumentalness`, `speechiness`, `liveness` | décimal 0-1 | Valeurs d'origine. |
| `loudness` | décimal | En décibels. |
| `tempo` | décimal | En battements par minute. |
| `spotify_url` | texte | `https://open.spotify.com/track/` suivi de `id`. |

L'application vérifie la présence de ces colonnes au chargement et affiche un
message clair si l'une d'elles manque.

## Familles de genres (proposition)

Un genre d'artiste appartient à une famille si l'un de ses mots figure dans la
liste de la famille :

| Famille | Mots reconnus |
|---|---|
| pop | pop |
| rock | rock |
| hip hop | « hip hop », rap, trap |
| jazz | jazz |
| classical | classical |
| electronic | electronic, electronica, electro, house, techno, edm, trance |

Exemple : un artiste « dance pop » et « pop rock » place ses titres dans pop et
dans rock. Le titre compte une fois dans le total, une fois dans chaque famille.

## Fonctions attendues

L'interface appelle ces fonctions sur la table **déjà filtrée**. Les noms sont
une proposition ; A reste libre de l'implémentation.

| Fonction (`src/metrics.py`) | Retour |
|---|---|
| `unique_tracks(df)` | entier : nombre de `id` distincts |
| `tracks_per_year(df)` | table `year`, `tracks` |
| `tracks_per_genre(df)` | table `genre`, `tracks` (un titre compte dans chacune de ses familles) |
| `genre_share(df)` | table `genre`, `tracks`, `share_pct` = 100 × titres de la famille / titres uniques |
| `yearly_change(df)` | table `year`, `tracks`, `change_pct` ; valeur absente si l'année précédente vaut 0 ou manque |
| `mean_features_by_year(df, features)` | table `year` + une colonne de moyenne par caractéristique |
| `mean_features_by_genre(df, features)` | table `genre` + une colonne de moyenne par caractéristique |

## Questions ouvertes pour A

1. La période 1960-2020 et les six familles conviennent-elles ?
2. Faut-il garder les titres sans famille dans un fichier à part, ou les
   exclure et les compter dans le rapport de qualité ?
3. Environ 2 % des artistes de `tracks.csv` sont absents de `artists.csv`
   (mesure sur un tirage de 20 000 titres) : les titres concernés sont-ils
   exclus ou gardés avec les genres des autres artistes ?
4. Des titres ont le même nom et les mêmes artistes sous des `id` différents
   (rééditions, remasters : 60 062 lignes concernées dans `tracks.csv`).
   Proposition : les garder, car ce sont des enregistrements distincts, et le
   dire dans les limites.
