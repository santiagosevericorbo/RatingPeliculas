import pandas as pd
from pathlib import Path
from tqdm import tqdm

from application.parser import GoodreadsParser
from infrastructure.repository import GoodreadsRepository


class GoodreadsImporter:
    """
    Responsabilidad única: orquestar la lectura del CSV y la
    persistencia. No sabe nada de SQL ni de parsing.
    """

    def __init__(self, parser: GoodreadsParser, repository: GoodreadsRepository):
        self.parser = parser
        self.repository = repository

    def run(self, csv_path: Path) -> None:
        df = pd.read_csv(csv_path)

        books = []
        readings = []

        for _, row in tqdm(df.iterrows(), total=len(df), desc="Parsing Goodreads CSV"):
            book, reading = self.parser.parse_row(row)
            books.append(self._book_tuple(book))
            readings.append(self._reading_tuple(reading))

        self.repository.save_books(books)
        self.repository.save_readings(readings)

        print(f"OK → {len(books)} libros importados desde {csv_path.name}")

    # --------------------------------------------------
    # mapeo domain → tuple para executemany
    # --------------------------------------------------

    def _book_tuple(self, b) -> tuple:
        return (
            b.goodreads_id,
            b.title,
            b.author,
            b.additional_authors,
            b.isbn,
            b.isbn13,
            b.publisher,
            b.binding,
            b.pages,
            b.year_published,
            b.year_original,
        )

    def _reading_tuple(self, r) -> tuple:
        return (
            r.goodreads_id,
            r.rating,
            r.status,
            r.date_read,
            r.date_added,
            r.shelves,
            r.read_count,
            r.review,
        )
