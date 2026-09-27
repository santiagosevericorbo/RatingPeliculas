from utils.sql_loader import load_sql


class LocalFileRepository:
    """
    Responsabilidad única: persistir LocalBooks en DuckDB.
    """

    def __init__(self, conn):
        self.conn = conn
        self.insert_query = load_sql("insert_book_local_file.sql")

    def save(self, rows: list[tuple]) -> None:
        self.conn.executemany(self.insert_query, rows)
