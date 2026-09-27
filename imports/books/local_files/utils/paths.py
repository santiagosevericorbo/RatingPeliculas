from pathlib import Path
from shared.config import BOOKS_DB

DB_PATH = BOOKS_DB
SQL_DIR = Path(__file__).resolve().parents[1] / "sql"
