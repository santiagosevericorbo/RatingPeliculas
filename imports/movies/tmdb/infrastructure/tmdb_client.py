import aiohttp


class TMDBClient:

    BASE_URL = "https://api.themoviedb.org/3/movie"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def fetch_watch_providers(self, session, tmdb_id):

        url = f"{self.BASE_URL}/{tmdb_id}/watch/providers"

        async with session.get(
            url,
            params={"api_key": self.api_key},
        ) as response:

            if response.status != 200:
                return None

            return await response.json()
