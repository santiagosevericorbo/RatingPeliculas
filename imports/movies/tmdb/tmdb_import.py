import requests
import pandas as pd
import time
from config import TMDB_API_KEY

API_KEY = TMDB_API_KEY

url = "https://api.themoviedb.org/3/discover/movie"

MAX_PAGES = 600  # ← controlás tamaño del crawl
TIMEOUT = 10  # segundos
SLEEP = 0.25  # evita rate limit

all_movies = []

# ---------- obtener total pages ----------
r = requests.get(url, params={"api_key": API_KEY}, timeout=TIMEOUT)

data = r.json()
total_pages = min(data["total_pages"], MAX_PAGES)

print(f"Fetching {total_pages} pages")

# ---------- crawl ----------
for page in range(1, total_pages + 1):

    try:
        params = {
            "api_key": API_KEY,
            "sort_by": "vote_count.desc",
            "page": page,
        }

        r = requests.get(url, params=params, timeout=TIMEOUT)

        if r.status_code == 429:
            print("Rate limit reached, sleeping...")
            time.sleep(5)
            continue

        r.raise_for_status()

        data = r.json()

        if not data["results"]:
            print("No more results, stopping early")
            break

        for m in data["results"]:
            all_movies.append(
                {
                    "tmdb_id": m["id"],
                    "title": m["title"],
                    "vote_average": m["vote_average"],
                    "vote_count": m["vote_count"],
                    "popularity": m["popularity"],
                    "release_date": m.get("release_date"),
                }
            )

        print(f"Page {page} OK")

        time.sleep(SLEEP)

    except requests.exceptions.RequestException as e:
        print(f"Error page {page}: {e}")
        continue


df = pd.DataFrame(all_movies)
df.to_parquet("data/tmdb/tmdb_movies.parquet", index=False)

print(f"OK - Saved {len(df)} movies")
