from pathlib import Path
import pandas as pd
import requests
from urllib.parse import urlparse
from tqdm import tqdm
import time

SAVE_EVERY = 20
# carpeta donde vive el script
BASE_DIR = Path(__file__).resolve().parent

# subir un nivel → rating peliculas/
PROJECT_ROOT = BASE_DIR.parent

INPUT = PROJECT_ROOT / "data" / "letterboxd" / "user-2026-05-01" / "watched.csv"
OUTPUT = (
    PROJECT_ROOT / "data" / "letterboxd" / "user-2026-05-01" / "watched_resolved.csv"
)
CHECKPOINT = (
    PROJECT_ROOT
    / "data"
    / "letterboxd"
    / "user-2026-05-01"
    / "checkpoint_letterboxd.csv"
)

df = pd.read_csv(INPUT)

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})


def resolve_slug(url, retries=3):

    for attempt in range(retries):
        try:
            r = session.get(url, allow_redirects=True, timeout=15)
            final_url = r.url

            parts = urlparse(final_url).path.strip("/").split("/")

            if "film" in parts:
                return parts[parts.index("film") + 1]

        except requests.exceptions.RequestException:
            print(f"Reintentando {url} ({attempt+1})")
            time.sleep(5)

    return None


results = []

for i, url in enumerate(tqdm(df["Letterboxd URI"])):

    slug = resolve_slug(url)
    results.append(slug)

    # checkpoint automático
    if i % SAVE_EVERY == 0:
        df.loc[:i, "lb_slug"] = results
        df.to_csv(CHECKPOINT, index=False)

df["lb_slug"] = results
df.to_csv(OUTPUT, index=False)

print("Proceso terminado correctamente")
