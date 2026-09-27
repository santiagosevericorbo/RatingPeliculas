import asyncio
import aiohttp
from utils.config import (
    HEADERS,
    TORRENTIO_BASE_URL,
    REQUEST_TIMEOUT,
    TORRENTIO_DELAY,
)


class TorrentioClient:

    BASE_URL = TORRENTIO_BASE_URL

    def __init__(self):
        self.lock = asyncio.Lock()
        self.last_request_time = 0

    async def _rate_limit(self):
        async with self.lock:
            now = asyncio.get_event_loop().time()
            wait = TORRENTIO_DELAY - (now - self.last_request_time)

            if wait > 0:
                await asyncio.sleep(wait)

            self.last_request_time = asyncio.get_event_loop().time()

    async def fetch_streams(self, session, imdb_id, retries=3):

        url = f"{self.BASE_URL}/stream/movie/{imdb_id}.json"

        for attempt in range(retries):

            try:
                await self._rate_limit()

                async with session.get(
                    url, headers=HEADERS, timeout=REQUEST_TIMEOUT
                ) as resp:

                    if resp.status == 429:
                        retry_after = int(resp.headers.get("Retry-After", 5))
                        print(f"[429] {imdb_id} retrying in {retry_after}s")
                        await asyncio.sleep(retry_after)
                        continue

                    if resp.status != 200:
                        text = await resp.text()
                        print(f"[ERROR {resp.status}] {imdb_id} | {text[:200]}")
                        return None

                    return await resp.json()

            except Exception as e:
                print(f"[EXCEPTION] {imdb_id} attempt {attempt+1} | {e}")
                await asyncio.sleep(2**attempt)

        return None
