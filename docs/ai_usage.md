# Utilisation de l'IA et vérifications

Ce journal décrit l'aide apportée par Codex (côté Assia) et par Claude Code
(côté Ines, dernière section). Il ne remplace pas la revue et l'explication
personnelle de chaque membre du binôme.

## Besoin formulé

Organiser un projet arXiv en binôme, répartir les tâches entre Assia (données
et calculs) et Ines (interface), puis continuer le travail avec des PR GitHub.

## Aide utilisée pour cette contribution

Codex a inspecté le code et les rapports locaux, exécuté les tests et recalculé
le bilan du Parquet réel avec `src.profile_data.build_profile`. Le résultat a
été comparé au rapport enregistré : 229 620 articles uniques, mêmes séries
annuelles et mêmes contrôles structurels. La suite locale compte 71 tests réussis.

Une formulation précédente assimilait « fusionné » à « intégré au produit ».
L'inspection des bases des PR a précisé que #12 et #15 sont fusionnées dans
`feat/arxiv-data-foundation`, tandis que la PR #10 vers `main` reste ouverte.
Cette distinction est nécessaire pour savoir quelle version est livrable.

## Limites conservées dans la documentation

- Le numéro de version Kaggle n'est pas connu. L'empreinte SHA-256 identifie
  le fichier réellement utilisé ; aucun numéro de version n'est inventé.
- Les catégories se recouvrent : leur somme ne constitue pas un total
  d'articles distincts et les parts peuvent dépasser 100 % au total.
- Les tests automatiques ne constituent pas une revue humaine de PR ni une
  vérification visuelle complète de l'application.
- Le bilan décrit des dépôts arXiv dans le périmètre choisi, sans mesurer
  leur qualité, leurs citations ou leur impact.

## À vérifier par les étudiantes

Ines reproduit les commandes du README avant d'approuver la contribution.
Assia doit pouvoir expliquer la date v1, le comptage unique et le calcul de
croissance annuelle. Chacune doit comprendre le code qu'elle présente.

## Finition de l'interface à la demande d'Assia

Codex a ajouté les graphiques Plotly en appelant les fonctions existantes de
`src.metrics` sur la table filtrée, puis rédigé le guide utilisateur et le scénario
de démonstration. Cinq tests supplémentaires vérifient les valeurs réellement
envoyées aux graphiques, les catégories qui se recouvrent, une période d'un an,
une recherche vide et le changement de filtres après pagination. La suite complète
compte 95 tests réussis. Cette aide n'est pas une contribution Git attribuée à Ines.
Elle doit relire la PR et comprendre les graphiques avant la présentation.

## Refonte visuelle demandée par Assia

Codex a retravaillé la hiérarchie, les couleurs, les cartes et les graphiques,
avec une identité bleu nuit et sauge. Les données et les fonctions de calcul
restent celles du projet. Les 95 tests passent. Le rendu a été contrôlé avec
Chromium sur ordinateur (1600 × 1200) et mobile (390 × 844), sans débordement
horizontal ; la navigation Comparaison et une recherche dans Exploration ont été
essayées. Les captures dans `docs/assets/` proviennent du navigateur et du vrai
snapshot. Cette vérification sur ce poste ne remplace pas l'essai sur celui d'Ines.

## Démonstrateur pour une enseignante

Après clarification de l'usage en classe, Codex a enrichi les analyses avec
calendrier mensuel, trajectoires par catégorie, Jaccard, combinaisons exclusives,
vocabulaire des titres et duel d'expressions. Le panier, les scénarios et les
questions à révéler permettent une démonstration participative.
Les 110 tests incluent des contrôles de dénominateurs sur un petit corpus dont
les résultats sont calculables à la main. Les deux agrégats exhaustifs du
calendrier et des combinaisons retrouvent 229 620 articles sur le vrai snapshot.
Les captures `showcase-*.jpg` proviennent de Chromium. Les analyses lexicales
sont descriptives ; aucune inférence sémantique ou mesure de qualité n'est annoncée.

## Interface et revues côté Ines

Claude Code a écrit les contributions d'Ines (#12, #13, #14) et exécuté les
contrôles avant chaque approbation des PR d'Assia. Demandes formulées :
construire des filtres qui partagent la même table avec tous les indicateurs,
prévoir le cas vide, puis tester les PR du binôme avant fusion.

Défauts détectés et corrections :

- **Mauvais jeu de données au départ.** Les trois premières PR (#8, #9, #11)
  portaient sur un autre dataset à la suite d'un lien erroné. Elles ont été
  fermées et refaites sur arXiv à partir du contrat de `docs/data_dictionary.md`.
- **Liste illisible sur les vraies données.** Sur les 229 620 articles, les
  titres et les auteurs, très longs, repoussaient la date et le lien hors de
  l'écran. Le défaut n'apparaissait pas sur les données fictives. Correction :
  largeur limitée des deux colonnes (#13).
- **Recherche sans accents abandonnée.** La première version neutralisait les
  accents avec une colonne de texte normalisé. Appliquée aux résumés, cette
  colonne aurait gardé en mémoire une seconde copie de tout le texte. La
  recherche ignore donc seulement la casse ; la limite est écrite dans la PR #13.
- **Fusion dans le mauvais ordre.** #17 a été fusionnée avant #18 : la refonte
  et les dix visualisations n'avaient pas atteint la branche commune. Le
  contrôle `git merge-base --is-ancestor` l'a montré avant la fusion vers
  `main` ; la PR #20 a rattrapé l'écart.

Vérification indépendante des données : le pipeline a été relancé sur le poste
d'Ines à partir d'un nouveau téléchargement Kaggle. L'empreinte SHA-256 de la
source, celle du Parquet et tous les compteurs sont identiques à ceux de
`reports/` (3 233 620 lignes lues, 229 620 articles retenus).
