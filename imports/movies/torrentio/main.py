import asyncio

from crawler.crawler import TorrentioCrawler
from crawler.client import TorrentioClient
from crawler.service import TorrentioService
from crawler.repository import TorrentRepository
from utils.duckdb_utils import get_connection
from utils.sql_loader import load_sql

db = get_connection()
db.execute(load_sql("create_movie_torrent_availability.sql"))
movies = db.query(load_sql("crawler_torrentio.sql")).to_df().to_dict("records")

crawler = TorrentioCrawler(
    client=TorrentioClient(),
    service=TorrentioService(),
    repository=TorrentRepository(db),
)

asyncio.run(crawler.run(movies))
