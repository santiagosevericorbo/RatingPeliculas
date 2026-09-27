import requests
import time
from pathlib import Path
import sys
from tqdm import tqdm

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))
from utils.sql_utils import load_sql
from utils.config import (
    HTML_DIR,
    REQUEST_SLEEP,
    DATA_DIR,
    SQL_DIR,
    HEADERS,
    SAVE_EVERY,
)

from utils.duckdb_utils import get_connection

HTML_DIR.mkdir(parents=True, exist_ok=True)
query_fetch = load_sql("2_fetch_candidates.sql")
session = requests.Session()
session.headers.update(HEADERS)


def download_page(url, retries=3):

    for attempt in range(retries):

        try:

            r = session.get(url, timeout=15)

            if r.status_code == 200:
                return r.text

        except requests.RequestException as e:

            print(f"\nRetry {attempt+1}: {e}")

            time.sleep(5)

    return None


def main():
    con = get_connection()

    rows = con.execute(query_fetch).fetchall()
    print(f"Películas a descargar: {len(rows)}")

    for imdb_id, slug in tqdm(rows):
        file = HTML_DIR / f"{imdb_id}.html"
        if file.exists():
            continue

        url = f"https://www.metacritic.com/movie/{slug}"
        html = download_page(url)
        if html:
            file.write_text(html, encoding="utf-8")

        time.sleep(REQUEST_SLEEP)

    con.close()


if __name__ == "__main__":
    main()
