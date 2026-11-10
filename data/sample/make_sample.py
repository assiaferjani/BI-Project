"""Fabrique le petit échantillon de démonstration utilisé par l'interface.

PROVISOIRE : ce script n'est pas le pipeline du projet. Il sert uniquement à
produire data/sample/tracks_sample.parquet, un fichier au format du contrat de
données (docs/data_contract.md), pour développer les écrans avant que
src/prepare_data.py existe. Les chiffres tirés de cet échantillon ne doivent
jamais être présentés comme des résultats.

Usage :
    python data/sample/make_sample.py --raw data/raw --output data/sample/tracks_sample.parquet
"""

from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path

import pandas as pd

START_YEAR, END_YEAR = 1960, 2020
SAMPLE_SIZE = 600
SEED = 42

# Proposition de familles de genres : un genre Spotify appartient à une famille
# si l'un de ses mots figure dans la liste. La règle finale est décidée avec A.
FAMILIES = {
    "pop": {"pop"},
    "rock": {"rock"},
    "hip hop": {"rap", "trap", "hip-hop", "hiphop"},
    "jazz": {"jazz"},
    "classical": {"classical"},
    "electronic": {"electronic", "electronica", "electro", "house", "techno", "edm", "trance"},
}

AUDIO = [
    "danceability", "energy", "valence", "acousticness", "instrumentalness",
    "speechiness", "liveness", "loudness", "tempo",
]


def families_of(genres: list[str]) -> list[str]:
    found = []
    for family, words in FAMILIES.items():
        for genre in genres:
            tokens = set(re.split(r"[\s]+", genre.lower()))
            if tokens & words or (family == "hip hop" and "hip hop" in genre.lower()):
                found.append(family)
                break
    return found


def precision_of(release_date: str) -> str:
    return {4: "year", 7: "month", 10: "day"}.get(len(release_date), "invalid")


def build(raw: Path) -> tuple[pd.DataFrame, dict]:
    tracks = pd.read_csv(raw / "tracks.csv", dtype={"id": str, "release_date": str})
    artists = pd.read_csv(raw / "artists.csv", dtype={"id": str}, usecols=["id", "genres"])
    genres_by_artist = {
        artist_id: ast.literal_eval(genres)
        for artist_id, genres in zip(artists["id"], artists["genres"])
        if genres != "[]"
    }

    tracks["year"] = tracks["release_date"].str[:4].astype(int)
    in_period = tracks[tracks["year"].between(START_YEAR, END_YEAR)].copy()

    in_period["artists"] = in_period["artists"].map(ast.literal_eval)
    in_period["artist_ids"] = in_period["id_artists"].map(ast.literal_eval)
    in_period["genres"] = in_period["artist_ids"].map(
        lambda ids: sorted({g for i in ids for g in genres_by_artist.get(i, [])})
    )
    in_period["selected_genres"] = in_period["genres"].map(families_of)
    in_scope = in_period[in_period["selected_genres"].map(len) > 0]

    stats = {
        "lignes_tracks": len(tracks),
        "dans_la_periode": len(in_period),
        "avec_une_famille": len(in_scope),
        "par_famille": in_scope["selected_genres"].explode().value_counts().to_dict(),
        "plusieurs_familles": int((in_scope["selected_genres"].map(len) > 1).sum()),
    }

    sample = in_scope.sample(SAMPLE_SIZE, random_state=SEED)
    sample["name"] = sample["name"].fillna("").str.strip()
    sample["release_precision"] = sample["release_date"].map(precision_of)
    sample["explicit"] = sample["explicit"].astype(bool)
    sample["spotify_url"] = "https://open.spotify.com/track/" + sample["id"]
    columns = [
        "id", "name", "artists", "artist_ids", "release_date", "release_precision",
        "year", "genres", "selected_genres", "popularity", "duration_ms", "explicit",
        *AUDIO, "spotify_url",
    ]
    return sample[columns].sort_values(["year", "id"]).reset_index(drop=True), stats


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--raw", type=Path, default=Path("data/raw"))
    parser.add_argument("--output", type=Path, default=Path("data/sample/tracks_sample.parquet"))
    args = parser.parse_args()

    sample, stats = build(args.raw)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sample.to_parquet(args.output, index=False)
    for key, value in stats.items():
        print(f"{key}: {value}")
    print(f"échantillon : {len(sample)} lignes -> {args.output}")


if __name__ == "__main__":
    main()
