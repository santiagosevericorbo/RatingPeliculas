import os
import asyncio
import aiohttp
import pandas as pd
from datetime import datetime, UTC
from tqdm import tqdm
from config import TMDB_API_KEY

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

API_KEY = TMDB_API_KEY
BASE_URL = "https://api.themoviedb.org/3/movie"

MOVIES_PATH = "data/tmdb/tmdb_movies.parquet"
PROVIDERS_PATH = "data/tmdb/tmdb_watch_providers.parquet"

WORKERS = 40
SAVE_EVERY = 1000

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

movies = pd.read_parquet(MOVIES_PATH)

if os.path.exists(PROVIDERS_PATH):
    existing = pd.read_parquet(PROVIDERS_PATH)
    processed_ids = set(existing["tmdb_id"].unique())
else:
    existing = pd.DataFrame()
    processed_ids = set()

pending_movies = movies[~movies["tmdb_id"].isin(processed_ids)]

print(f"{len(pending_movies)} movies pending")

# --------------------------------------------------
# GLOBAL STATE
# --------------------------------------------------

queue = asyncio.Queue()
results = []
lock = asyncio.Lock()
progress = None

# --------------------------------------------------
# FETCH
# --------------------------------------------------


async def fetch_provider(session, tmdb_id):

    url = f"{BASE_URL}/{tmdb_id}/watch/providers"

    retries = 0

    while retries < 5:

        async with session.get(
            url,
            params={"api_key": API_KEY},
        ) as response:

            if response.status == 429:
                await asyncio.sleep(2**retries)
                retries += 1
                continue

            if response.status != 200:
                return

            data = await response.json()
            uy = data.get("results", {}).get("UY")

            if not uy:
                return

            rows = []

            for offer_type in ["flatrate", "rent", "buy"]:
                for p in uy.get(offer_type, []):

                    rows.append(
                        {
                            "tmdb_id": tmdb_id,
                            "country": "UY",
                            "provider_id": p["provider_id"],
                            "provider_name": p["provider_name"],
                            "logo_path": p["logo_path"],
                            "type": offer_type,
                            "last_update": datetime.now(UTC),
                        }
                    )

            async with lock:
                results.extend(rows)

            return


# --------------------------------------------------
# WORKER
# --------------------------------------------------


async def worker(session):

    global results, existing

    while True:

        tmdb_id = await queue.get()

        try:
            await fetch_provider(session, tmdb_id)

            progress.update(1)

            if len(results) >= SAVE_EVERY:
                save_checkpoint()

        finally:
            queue.task_done()


# --------------------------------------------------
# SAVE
# --------------------------------------------------


def save_checkpoint():

    global results, existing

    if not results:
        return

    df = pd.DataFrame(results)

    if not existing.empty:
        existing = pd.concat([existing, df], ignore_index=True)
    else:
        existing = df

    existing.to_parquet(PROVIDERS_PATH, index=False)

    print(f"Checkpoint saved ({len(existing)} rows)")

    results = []


# --------------------------------------------------
# MAIN
# --------------------------------------------------


async def main():

    global progress

    for tmdb_id in pending_movies["tmdb_id"]:
        await queue.put(tmdb_id)

    connector = aiohttp.TCPConnector(limit=WORKERS)
    timeout = aiohttp.ClientTimeout(total=30)

    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
    ) as session:

        workers = [asyncio.create_task(worker(session)) for _ in range(WORKERS)]

        progress = tqdm(total=queue.qsize(), desc="Fetching UY providers")

        await queue.join()

        for w in workers:
            w.cancel()

    save_checkpoint()


# --------------------------------------------------

if __name__ == "__main__":
    asyncio.run(main())
    print("Providers updated incrementally")
