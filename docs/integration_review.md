# Vérification du travail publié par Ines

> Relevé historique : les états des PR et les validations ci-dessous décrivent
> l'essai initial. Les PR #12 et #15 ont depuis été fusionnées dans
> `feat/arxiv-data-foundation`, et le vrai snapshot a été traité et contrôlé.
> Le bilan actuel des données réelles se trouve dans [data_findings.md](data_findings.md).

Vérification du 10 novembre 2026 sur les branches GitHub disponibles à cette date.
Ce relevé porte sur du code publié, pas sur d'éventuels changements locaux d'Ines.

## Contributions examinées

| PR | Travail | Révision examinée |
| --- | --- | --- |
| [#12](https://github.com/assiaferjani/BI-Project/pull/12) | Chargement Parquet, filtres et quatre onglets Streamlit | `b3481fbc6a3f5bfbee3c86a22b6ce2c6659d8590` |
| [#13](https://github.com/assiaferjani/BI-Project/pull/13) | Recherche littérale, pagination, fiche article et export CSV | `ace492f7f41e828db77295def50fbf4ce0322463` |
| [#14](https://github.com/assiaferjani/BI-Project/pull/14) | Conception des écrans et proposition des fonctions de calcul | `8330802ceb98d0d99b68003b13bcb6f39577ac12` |

La branche #13 contient aussi les changements de #12. Son code a été extrait dans
un répertoire temporaire pour vérification sans modifier les branches d'Ines.
Les cinq noms de fonctions proposés dans #14 sont repris par `src/metrics.py`.

## Vérifications exécutées

- Suite de la branche d'Ines #13 : **57 tests réussis**, dont les 20 du pipeline.
- Partie A avec les indicateurs : **39 tests réussis**, dont 19 sur les indicateurs.
- Copie temporaire réunissant le code d'Ines et les nouvelles fonctions :
  **76 tests réussis**. Le pipeline commun n'est compté qu'une fois.
- Cas d'intégration avec 60 articles fictifs : application des filtres d'Ines
  (2020–2023, cs.AI, recherche « TRANSFORMERS »), puis calculs d'Assia et export.
  Résultat attendu et obtenu : 6 articles uniques, série annuelle 3/0/0/3,
  cs.AI = 6 (100 %), cs.LG = 3 (50 %), export de 6 lignes. La variation de
  2023 reste non calculable car 2022 vaut zéro.

Les tests d'Ines couvrent notamment le démarrage Streamlit, l'absence de fichier,
les filtres, la recherche sans résultat et avec ponctuation, la page 2 et une
fiche sans résumé. Le mode démonstration affiche un avertissement et masque
les liens des articles fictifs dans l'interface.

## À faire ensuite

Les fonctions de calcul sont compatibles avec les sorties des filtres. Ines peut
les relier aux graphiques avec les appels de [metrics.md](metrics.md). Les graphiques
ne sont pas encore présents dans la révision de son interface examinée ici.

Les PR sont encore à relire par le binôme avant fusion. Les branches de travail
sont empilées : #12 et #14 reposent sur #10 ; #13 repose sur #12 ; la PR des
indicateurs repose également sur #10. Après fusion de #10, il faudra vérifier
les bases des PR restantes et leur diff avant leurs fusions respectives.

Le snapshot Kaggle réel reste à récupérer et à vérifier. Les tests effectués
utilisent des données fictives ; ils ne valident ni les chiffres du vrai dataset
ni les performances sur son volume complet. Ce relevé ne constitue pas une
approbation GitHub et aucune branche d'Ines n'a été fusionnée par cette vérification.
