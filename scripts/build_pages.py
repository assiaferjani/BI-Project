"""Version statique de l'application pour GitHub Pages.

GitHub Pages ne sert que des fichiers : l'application Streamlit y tourne dans le
navigateur grâce à stlite (Python compilé en WebAssembly). Deux commandes :

    python scripts/build_pages.py slim    # données en ligne, sans les résumés
    python scripts/build_pages.py site    # dossier _site/ à publier

`slim` se lance à la main quand le fichier préparé change ; son résultat
(`pages/data/articles.parquet`) est versionné. `site` est lancé par le workflow
`.github/workflows/pages.yml`.
"""

from __future__ import annotations

import argparse
import json
import shutil
import tomllib
import zipfile
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed" / "articles.parquet"
ONLINE_DATA = ROOT / "pages" / "data" / "articles.parquet"
TEMPLATE = ROOT / "pages" / "index.html"
CONFIG = ROOT / ".streamlit" / "config.toml"
CONFIG_MARKER = "__STREAMLIT_CONFIG__"
# Code de l'application embarqué dans le navigateur (Python et feuille de style).
APP_SOURCES = ["app.py", "ui", "src"]


def slim(source: Path, output: Path) -> int:
    """Copie le fichier préparé en vidant les résumés ; renvoie le nombre d'articles.

    Les résumés pèsent 85 % du fichier. La colonne reste présente, avec des
    chaînes vides, pour que le contrat de données de l'interface soit respecté.
    """
    table = pq.read_table(source)
    position = table.schema.get_field_index("abstract")
    empty = pa.array([""] * table.num_rows, type=table.schema.field(position).type)
    table = table.set_column(position, table.schema.field(position), empty)
    output.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, output, compression="zstd", compression_level=19)
    return table.num_rows


def streamlit_config(path: Path = CONFIG) -> dict[str, object]:
    """Options de `.streamlit/config.toml` au format à plat attendu par stlite."""
    sections = tomllib.loads(path.read_text(encoding="utf-8"))
    return {
        f"{section}.{key}": value
        for section, options in sections.items()
        for key, value in options.items()
    }


def build_site(output: Path, data: Path = ONLINE_DATA) -> None:
    """Assemble la page, le code de l'application et les données dans `output`."""
    if not data.exists():
        raise SystemExit(f"{data} est absent : lancer d'abord la commande « slim ».")
    if output.exists():
        shutil.rmtree(output)
    (output / "data").mkdir(parents=True)

    page = TEMPLATE.read_text(encoding="utf-8")
    config = {**streamlit_config(), "client.toolbarMode": "viewer"}
    page = page.replace(CONFIG_MARKER, json.dumps(config, ensure_ascii=False, indent=2))
    (output / "index.html").write_text(page, encoding="utf-8")

    with zipfile.ZipFile(output / "app.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for name in APP_SOURCES:
            path = ROOT / name
            files = [path] if path.is_file() else sorted(path.rglob("*"))
            for file in files:
                if file.is_file() and "__pycache__" not in file.parts:
                    archive.write(file, file.relative_to(ROOT).as_posix())

    shutil.copyfile(data, output / "data" / "articles.parquet")
    # Sans ce fichier, GitHub Pages passerait le site dans Jekyll.
    (output / ".nojekyll").touch()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    slim_parser = commands.add_parser("slim", help="écrire les données en ligne sans résumés")
    slim_parser.add_argument("--input", type=Path, default=PROCESSED)
    slim_parser.add_argument("--output", type=Path, default=ONLINE_DATA)
    site_parser = commands.add_parser("site", help="assembler le dossier à publier")
    site_parser.add_argument("--output", type=Path, default=ROOT / "_site")
    args = parser.parse_args()

    if args.command == "slim":
        count = slim(args.input, args.output)
        size = args.output.stat().st_size / 1e6
        print(f"{args.output} : {count} articles, {size:.1f} Mo")
    else:
        build_site(args.output)
        print(f"Site assemblé dans {args.output}")


if __name__ == "__main__":
    main()
