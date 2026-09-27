from pathlib import Path
import requests
import time
import re
import sys
import pandas as pd
from tqdm import tqdm
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))
from utils.sql_utils import load_sql
from utils.config import (
    DATA_DIR,
    SQL_DIR,
    HEADERS,
    CHECKPOINT,
    SAVE_EVERY,
    REQUEST_SLEEP,
)
from utils.duckdb_utils import get_connection

session = requests.Session()
session.headers.update(HEADERS)

query_discover = load_sql("0_discover_candidates.sql")
query_create = load_sql("1_slug_candidates.sql")


def normalize_title(title: str) -> str:
    title = title.lower()
    title = re.sub(r"[^\w\s-]", "", title)
    title = title.replace("&", "and")
    title = title.replace(" ", "-")
    return title


def slug_exists(slug: str) -> bool:

    url = f"https://www.metacritic.com/movie/{slug}"

    try:

        r = session.get(url, timeout=15)
        return r.status_code == 200

    except requests.RequestException:
        return False


def save_checkpoint(results):

    if not results:
        return

    df = pd.DataFrame(
        results,
        columns=[
            "imdb_id",
            "title_norm",
            "year",
            "slug",
            "confidence",
        ],
    )

    df.to_csv(CHECKPOINT, index=False)

    print(f"Checkpoint guardado: {len(results)} registros")


def main():

    con = get_connection()

    movies = con.execute(query_discover).fetchall()
    print(query_discover)
    print(con.execute(query_discover).fetchdf().head())
    print(f"Películas a procesar: {len(movies)}")

    results = []

    if CHECKPOINT.exists():

        checkpoint_df = pd.read_csv(CHECKPOINT)

        results = checkpoint_df.values.tolist()

        processed_ids = set(checkpoint_df["imdb_id"])

        print(f"Checkpoint encontrado: {len(processed_ids)} películas")

    for i, row in enumerate(tqdm(movies)):

        imdb_id = row[0]
        if imdb_id in processed_ids:
            continue
        title = row[1]
        year = row[2]
        slug = normalize_title(title)

        if slug_exists(slug):
            results.append((imdb_id, title, year, slug, 1.0))
            processed_ids.add(imdb_id)

        if i > 0 and i % SAVE_EVERY == 0:
            save_checkpoint(results)

        time.sleep(REQUEST_SLEEP)

    print("Guardando resultados finales...")

    con.execute(query_create)

    con.executemany(
        "INSERT INTO metacritic_slug_candidates VALUES (?, ?, ?, ?, ?)",
        results,
    )

    save_checkpoint(results)

    con.close()

    print("Discover terminado")


if __name__ == "__main__":
    main()
