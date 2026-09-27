from shared.config import GOODREADS_CSV
from utils.duckdb_utils import get_connection
from utils.sql_loader import load_sql

from application.parser import GoodreadsParser
from application.importer import GoodreadsImporter
from infrastructure.repository import GoodreadsRepository

db = get_connection()
db.execute(load_sql("create_tables.sql"))

importer = GoodreadsImporter(
    parser=GoodreadsParser(),
    repository=GoodreadsRepository(db),
)

importer.run(GOODREADS_CSV)
