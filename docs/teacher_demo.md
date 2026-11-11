# Présenter arXiv Explorer en classe

Ce démonstrateur vise à donner envie d'explorer les données tout en montrant
comment justifier un résultat. Il utilise les métadonnées réelles d'arXiv du
snapshot documenté, filtrées sur 2020–2024 et cs.AI, cs.LG, cs.CL.

## Préparer la séance

Lancer `python -m streamlit run app.py` depuis la racine du dépôt, après
l'installation et la préparation décrites dans le README. Avec le snapshot
étudié, le panorama doit afficher 229 620 articles. Vérifier l'absence de bandeau
fictif. Le mode de démonstration à trois articles sert aux essais techniques.

Activer **Mode projection** dans la barre latérale : introduction plus compacte
et textes d'accompagnement agrandis. Les scénarios en un clic changent les filtres
communs. **Panorama** rétablit le corpus entier ; **Enquête · transformer** retient
cs.CL, 2023–2024 et l'expression `transformer` dans les titres ou résumés.

## Un parcours de 12 à 15 minutes

| Temps | Espace et manipulation | Question à poser |
| --- | --- | --- |
| 2 min | Vue d'ensemble : courbe, croissance, calendrier et carte des communautés | Que compte-t-on exactement ? |
| 3 min | Tendances : calendrier brut puis %, trajectoires puis base 100 | Le plus gros domaine est-il celui qui progresse le plus vite ? |
| 2 min | Comparaison : intersection puis Jaccard, combinaisons exactes | Pourquoi la somme des catégories dépasse-t-elle le total ? |
| 3 min | Vocabulaire : transformer contre diffusion, effectifs puis taux | Le mot progresse-t-il plus vite que le corpus ? |
| 2 min | Exploration : article aléatoire, fiche, ajout au panier, export | Comment retourner du graphique aux observations ? |
| 2 min | Atelier puis Méthode : hypothèse, preuve, limites | Qu'est-ce qu'une conclusion que ces données ne permettent pas ? |

Les questions « À vous de jouer » permettent de solliciter la classe avant de
révéler une piste de réponse. Les réponses numériques utilisent la sélection
courante. Le panier est indépendant des filtres mais propre à la session :
exporter le CSV pour conserver la sélection.

## Les dix visualisations et leur rôle

| Visualisation | Unité et lecture |
| --- | --- |
| Dépôts annuels | Articles uniques par année de première soumission v1 |
| Variation annuelle | 100 × (N − N précédent) / N précédent ; base nulle non calculable |
| Volumes par catégorie | Articles uniques portant chaque code ; recouvrements possibles |
| Carte thermique mensuelle | Effectifs par année et mois ; option part du total de chaque année |
| Trajectoires comparées | Effectifs par catégorie ; option première année filtrée = 100 |
| Calendrier des dépôts | Somme des articles par mois sur les années retenues |
| Matrice de recouvrement | Intersection en articles ; option intersection / union × 100 |
| Carte des combinaisons | Catégories étudiées exactes : chaque article dans un seul rectangle |
| Vocabulaire | Titres contenant un mot, une seule fois par titre |
| Duel d'expressions | Titres contenant une expression ; option pour 1 000 articles de l'année |

Le panorama reprend le calendrier et les combinaisons. Il y a donc dix
visualisations distinctes et douze graphiques rendus dans l'application complète.
Les tableaux numériques et les CSV permettent de contrôler les résultats.

## Interactions à faire essayer aux étudiants

- Choisir une période et des catégories ; garder la même question puis changer
  une seule hypothèse à la fois.
- Basculer entre les effectifs et un indicateur normalisé ; expliquer le
  dénominateur et les cas non calculables.
- Exclure un mot du classement, puis utiliser un mot comme filtre global.
- Comparer deux expressions littérales ; essayer de vider l'une d'elles.
- Tirer un article au hasard dans la sélection, ouvrir sa fiche et l'ajouter au
  panier. Changer les filtres et constater que le panier est conservé.
- Exporter un résultat et vérifier son nombre d'identifiants uniques.

## Limites à montrer plutôt qu'à cacher

Le vocabulaire repose sur des séquences a–z de quatre lettres ou plus dans les
titres et sur une liste explicite de mots exclus. Ce n'est ni un modèle de sujets,
ni une mesure d'importance scientifique. Le duel porte sur les titres, tandis que
la recherche globale porte sur les titres et les résumés : les effectifs peuvent
donc différer pour une même expression.

Le calendrier agrège les mois sans correction du nombre de jours, des jours
ouvrés ou des années partielles. Une différence ne prouve pas une saisonnalité.
La base 100 est non calculable pour une catégorie absente de la première année
filtrée. Les années sans article ont un taux lexical non calculable.

Les catégories du corpus se recouvrent. Une combinaison exacte concerne seulement
les trois catégories étudiées, pas toutes les étiquettes originales d'arXiv.
Les publications, leur qualité, les citations et l'impact ne sont pas équivalents.

## Ce que l'exemple peut inspirer

On peut demander aux étudiants de choisir leur question, définir l'unité de
comptage, construire une interaction utile, vérifier un calcul à la main et
expliquer une limite. Le projet montre aussi le travail par branches et PR,
les tests sur petits jeux contrôlés et la vérification sur les données réelles.
La quantité de graphiques n'est pas un critère de qualité à elle seule.
