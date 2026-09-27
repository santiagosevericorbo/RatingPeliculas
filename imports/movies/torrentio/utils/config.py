from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = ROOT_DIR.parents[1]
DATA_DIR = PROJECT_DIR / "data"
SQL_DIR = ROOT_DIR / "sql"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://torrentio.strem.fun/",
}
TORRENTIO_BASE_URL = "https://torrentio.strem.fun"
TORRENTIO_PROVIDERS = ["yts", "rarbg", "1337x", "thepiratebay"]
TORRENTIO_CONFIG = "sort=seeders"
REQUEST_TIMEOUT = 20
WORKERS = 20
SAVE_EVERY = 500
TORRENTIO_DELAY = 0.5
