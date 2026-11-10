# Démonstration proposée : 6 à 8 minutes

Répéter ensemble avec les mêmes filtres et le même snapshot. Les valeurs
ci-dessous concernent uniquement le fichier identifié dans le manifeste.

| Durée | Intervenante | Démonstration |
| --- | --- | --- |
| 1 minute | Ensemble | Question, public étudiant et choix d'arXiv. |
| 2 minutes | Assia | Préparation progressive, date v1, 229 620 articles et comptage unique. |
| 2 à 3 minutes | Ines | Filtres, graphiques, recherche, fiche et export. |
| 1 à 2 minutes | Ensemble | Tests, une PR relue, limites et aide de l'IA. |

## Parcours à montrer

1. Ouvrir l'application avec les vraies données. Vérifier l'absence de bandeau
   fictif et supprimer toute recherche. Toutes les années, aucune catégorie
   sélectionnée : 229 620 articles. Montrer la courbe annuelle et le tableau.
2. Expliquer la hausse de 2024 : de 51 037 à 67 321 dépôts, soit environ
   +31,91 %. Cette hausse ne mesure pas une amélioration de qualité scientifique.
3. Montrer la comparaison : cs.CL = 58 471, cs.AI = 89 660 et cs.LG = 153 967.
   Expliquer pourquoi la somme dépasse le total d'articles uniques.
4. Choisir cs.CL puis 2023–2024, saisir `transformer` : 3 260 articles.
   Le total, la courbe et la comparaison doivent changer ensemble.
5. Ouvrir une fiche d'article, puis exporter. Vérifier les 3 260 lignes de données
   dans le CSV. Le fichier comprend toutes les pages.
6. Saisir une expression improbable, par exemple `[aucun article zzzz]`.
   Montrer le message de résultat vide ; effacer ensuite la recherche.
7. Montrer une PR réellement relue et la suite de tests. Expliquer un cas
   contrôlé : six articles, deux catégories qui se recouvrent, export de six lignes.

## Questions à préparer toutes les deux

- Pourquoi la date v1 plutôt que la date de mise à jour ?
- Pourquoi des parts peuvent-elles dépasser 100 % au total ?
- Que signifie « non calculable » pour une variation ?
- Comment reproduire le sous-ensemble avec le même fichier ?
- Quelle vérification a permis de valider une suggestion de l'IA ?

## Attribution et vérifications finales

La préparation des graphiques et de ces guides a été assistée par Codex à la
demande d'Assia. Ines doit les relire, les utiliser et comprendre leurs calculs
avant de les présenter. Les commits gardent l'identité Git de leur auteur.

Avant la présentation : revoir visuellement l'interface sur les deux postes,
ouvrir le CSV dans un tableur, préparer quelques captures de l'application et
reproduire l'installation depuis une copie neuve. Ne pas annoncer ces actions
comme effectuées tant qu'elles ne l'ont pas été.
