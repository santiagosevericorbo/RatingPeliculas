from shared.duckdb_utils import get_connection as _get_connection
from utils.paths import DB_PATH
import duckdb


def get_connection() -> duckdb.DuckDBPyConnection:
    return _get_connection(DB_PATH)
