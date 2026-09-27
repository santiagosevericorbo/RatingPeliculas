import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))  # Ratings Peliculas
sys.path.insert(0, str(Path(__file__).resolve().parent))  # local_files/
print(Path(__file__).resolve())
print(Path(__file__).resolve().parents)
print(sys.path)
from shared.config import BOOKS_ROOT
from shared.runner import Runner
from utils.duckdb_utils import get_connection
from utils.sql_loader import load_sql

from application.scanner import LocalBookScanner
from application.matcher import GoodreadsMatcher
from application.importer import LocalFileImporter
from infrastructure.repository import LocalFileRepository

db = get_connection()
db.execute(load_sql("create_book_local_file.sql"))

importer = LocalFileImporter(
    scanner=LocalBookScanner(BOOKS_ROOT),
    matcher=GoodreadsMatcher(db),
    repository=LocalFileRepository(db),
)

with Runner():
    importer.run()
