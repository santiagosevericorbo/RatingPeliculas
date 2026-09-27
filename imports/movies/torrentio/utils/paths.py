from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]

DB_PATH = BASE_DIR / "db" / "movies.duckdb"
