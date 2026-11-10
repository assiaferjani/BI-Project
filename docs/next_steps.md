# Prochaines étapes

## Assia — personne A

1. Comprendre `normalize` et les règles de dates, catégories et doublons.
2. Faire relire cette contribution à Ines avant de la fusionner.
3. Télécharger le snapshot Kaggle, noter sa version et lancer le traitement réel.
4. Vérifier le rapport : volumes, exclusions et quelques articles à la main.
5. Ouvrir une PR avec les observations de qualité et le dictionnaire corrigé
   si le vrai fichier révèle des différences ; ne pas commiter les gros fichiers.
6. Dans une branche `feat/metrics`, développer les calculs et leurs tests.

## Ines — personne B

1. Cloner le dépôt et récupérer la branche proposée pour la revue.
2. Suivre les commandes de démonstration du README et exécuter les tests.
3. Confirmer les colonnes et proposer une maquette des écrans.
4. Après fusion, partir de `main` à jour dans une branche `feat/app-filters`.
5. Ajouter Streamlit, construire le chargement et les filtres ; gérer les données
   absentes et les résultats vides. Étiqueter explicitement toute démonstration fictive.
6. Ajouter graphiques, recherche et export dans de petites PR relues par Assia.

## À décider ensemble

- Valider les trois catégories et la période proposées.
- Choisir la version exacte du snapshot utilisée sur les deux ordinateurs.
- Confirmer les conventions des filtres et le scénario de présentation.
