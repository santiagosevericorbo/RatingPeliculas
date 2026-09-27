from utils.sql_loader import load_sql


class GoodreadsRepository:
    """
    Responsabilidad única: persistir Books y BookReadings en DuckDB.
    """

    def __init__(self, conn):
        self.conn = conn
        self.insert_book = load_sql("insert_book.sql")
        self.insert_reading = load_sql("insert_book_reading.sql")

    def save_books(self, rows: list[tuple]) -> None:
        self.conn.executemany(self.insert_book, rows)

    def save_readings(self, rows: list[tuple]) -> None:
        self.conn.executemany(self.insert_reading, rows)
