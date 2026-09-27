from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from utils.sql_utils import load_sql
from utils.config import (
    SQL_DIR,
)

from utils.duckdb_utils import get_connection

query_load = load_sql("4_load.sql")


def main():

    con = get_connection()

    con.execute(query_load)

    con.close()


if __name__ == "__main__":
    main()
