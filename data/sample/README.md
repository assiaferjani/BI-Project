# Échantillon de démonstration

`tracks_sample.parquet` contient 600 titres tirés au hasard (graine 42) parmi
les titres 1960-2020 qui ont au moins une famille de genres. Il respecte le
format décrit dans `docs/data_contract.md`.

Il sert uniquement à développer et tester l'interface sans le fichier complet.
**Aucun chiffre tiré de cet échantillon n'est un résultat du projet.**
L'application affiche un bandeau quand elle l'utilise.

Pour le régénérer, après avoir placé `tracks.csv` et `artists.csv` dans
`data/raw/` :

```
python data/sample/make_sample.py
```

`make_sample.py` est un outil provisoire de B. Le pipeline du projet est
`src/prepare_data.py` (membre A) ; quand il existera, l'échantillon sera
produit à partir de sa sortie.
