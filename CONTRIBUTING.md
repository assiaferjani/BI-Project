# Travailler à deux

Assia est la personne A ; Ines est la personne B. Chacune doit comprendre les
données, un calcul et un choix de conception, et relire les PR de l'autre.

## Une branche par tâche

Depuis un répertoire de travail sans modification en attente :

```bash
git switch main
git pull --ff-only origin main
git switch -c feat/nom-de-la-tache
```

Développer, puis exécuter `python -m pytest`. Consulter `git diff` et `git status`,
ajouter seulement les fichiers utiles avec `git add chemin/du/fichier`, faire
un commit explicite et publier la branche avec `git push -u origin NOM_BRANCHE`.

## Ouvrir et relire la PR

Sur GitHub : Pull requests → New pull request ; base `main`, branche de la tâche.
Décrire le problème, le changement et les vérifications réellement exécutées.
Une PR brouillon permet une première discussion ; la passer prête quand elle
peut être revue. L'autre personne lit les modifications et reproduit les tests.

Les corrections sont poussées sur la même branche. Après approbation, fusionner
la PR puis mettre à jour `main` localement. Ne pas fusionner sa propre PR sans
la revue de l'autre. Les réglages de protection dépendent de l'offre GitHub.

Ne jamais ajouter le gros fichier Kaggle, `.venv`, les sorties de traitement
ou les identifiants d'accès. Pour modifier les dépendances, éditer
`requirements.in` et régénérer `requirements.txt` avec `uv pip compile`.
