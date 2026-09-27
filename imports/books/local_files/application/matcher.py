from typing import Optional
import duckdb

from domain.local_book import LocalBook


class GoodreadsMatcher:
    """
    Responsabilidad única: intentar resolver el goodreads_id de un
    LocalBook cruzando título/autor contra la tabla book ya importada.
    """

    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn

    def match(self, book: LocalBook) -> Optional[int]:
        """
        Busca en la tabla book por similitud de título.
        Retorna goodreads_id si encuentra match único, None si no.
        """
        result = self.conn.execute(
            """
            SELECT goodreads_id
            FROM   book
            WHERE  lower(title) = lower(?)
            LIMIT  1
            """,
            [book.title_guess],
        ).fetchone()

        if result:
            return result[0]

        # segundo intento: búsqueda parcial
        result = self.conn.execute(
            """
            SELECT goodreads_id
            FROM   book
            WHERE  lower(title) LIKE lower(?)
            LIMIT  1
            """,
            [f"%{book.title_guess}%"],
        ).fetchone()

        return result[0] if result else None
