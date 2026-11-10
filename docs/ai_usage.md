# Utilisation de l'IA et vérifications

Ce journal décrit l'aide apportée par Codex dans cette contribution. Il ne
remplace pas la revue et l'explication personnelle de chaque membre du binôme.

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
