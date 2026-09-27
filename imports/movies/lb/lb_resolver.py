from urllib.parse import urlparse
import requests
import time
import pandas as pd
from tqdm import tqdm

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})


def resolve_slug(url, retries=3):

    for _ in range(retries):
        try:
            r = session.get(url, allow_redirects=True, timeout=15)
            final = r.url

            parts = urlparse(final).path.strip("/").split("/")

            if "film" in parts:
                return parts[parts.index("film") + 1]

        except requests.exceptions.RequestException:
            time.sleep(5)

    return None


def process_csv(input_path, output_path, uri_column):

    df = pd.read_csv(input_path)

    slugs = []

    for url in tqdm(df[uri_column], desc=input_path.name):
        slugs.append(resolve_slug(url))
        time.sleep(0.5)

    df["lb_slug"] = slugs
    df.to_csv(output_path, index=False)

    print(f"OK -> {output_path}")
