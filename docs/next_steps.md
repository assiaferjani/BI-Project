# Prochaines étapes

## Usage en classe

La branche `feat/arxiv-teaching-showcase` enrichit le projet en démonstrateur pour
une enseignante. Le parcours actuel est décrit dans `docs/teacher_demo.md` : dix
visualisations, huit espaces, scénarios, questions et panier de lecture. Les 110
tests passent, et le parcours a été contrôlé dans Chromium sur ordinateur et mobile.
Le plan de binôme ci-dessous conserve les responsabilités du projet d'origine.
Pour présenter cet exemple, lancer le scénario Panorama, activer le mode projection,
puis suivre le guide enseignant. La version Kaggle exacte reste à retrouver ;
le fichier réellement utilisé est identifié par son empreinte.


## Assia — personne A

1. Lire `docs/data_findings.md` : le snapshot est traité, les calculs testés et
   les premiers chiffres réels vérifiés.
2. Savoir expliquer la date v1, les 229 620 articles uniques, les catégories
   qui se recouvrent et une variation annuelle.
3. Retrouver le numéro de version Kaggle si possible ; l'empreinte exacte du
   snapshot est déjà conservée dans le manifeste.
4. Faire relire le bilan et les contrôles à Ines, puis suivre la fusion des PR.
5. Vérifier quelques articles à la main et préparer une explication des limites.

## Ines — personne B

1. Relire les PR #10 et #16 : les PR de conception #14 et de recherche/export
   #13 sont déjà fusionnées dans `feat/arxiv-data-foundation`. Utiliser
   `docs/review_checklist.md` pour reproduire les contrôles.
2. Relire et essayer les graphiques désormais branchés sur `src.metrics`,
   ainsi que `docs/user_guide.md` et `docs/demo_script.md`.
3. Utiliser le même snapshot sur son poste et vérifier les chiffres du bilan réel.
4. Tester visuellement le parcours et ouvrir l'export dans un tableur.
5. Finaliser les captures, les instructions de lancement et le scénario de démo.

## À décider ensemble

- Valider les trois catégories et la période proposées.
- Choisir la version exacte du snapshot utilisée sur les deux ordinateurs.
- Confirmer les conventions des filtres et le scénario de présentation.
