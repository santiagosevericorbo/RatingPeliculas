from shared.sql_loader import load_sql as _load_sql
from utils.paths import SQL_DIR


def load_sql(name: str) -> str:
    return _load_sql(SQL_DIR, name)
