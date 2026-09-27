import pandas as pd
import asyncio

from config import TMDB_API_KEY
from infrastructure.tmdb_client import TMDBClient
from infrastructure.parquet_repository import ProviderRepository
from application.provider_service import ProviderService
from application.crawler import ProviderCrawler
from constants import MOVIES_PATH, PROVIDERS_PATH

movies = pd.read_parquet(MOVIES_PATH)

repo = ProviderRepository(PROVIDERS_PATH)
processed = repo.load_existing_ids()

pending = movies[~movies["tmdb_id"].isin(processed)]

client = TMDBClient(TMDB_API_KEY)
service = ProviderService()

crawler = ProviderCrawler(client, repo, service)

asyncio.run(crawler.run(pending["tmdb_id"]))
