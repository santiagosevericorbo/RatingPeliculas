import re
import pandas as pd
from datetime import date
from typing import Optional, Tuple

from domain.book import Book, BookReading


class GoodreadsParser:
    """
    Responsabilidad única: transformar una fila del CSV de Goodreads
    en los domain objects Book y BookReading.
    """

    def parse_row(self, row: pd.Series) -> Tuple[Book, BookReading]:
        book = Book(
            goodreads_id=int(row["Book Id"]),
            title=row["Title"],
            author=row["Author"],
            additional_authors=self._optional_str(row.get("Additional Authors")),
            isbn=self._clean_isbn(row.get("ISBN")),
            isbn13=self._clean_isbn(row.get("ISBN13")),
            publisher=self._optional_str(row.get("Publisher")),
            binding=self._optional_str(row.get("Binding")),
            pages=self._optional_int(row.get("Number of Pages")),
            year_published=self._optional_int(row.get("Year Published")),
            year_original=self._optional_int(row.get("Original Publication Year")),
        )

        reading = BookReading(
            goodreads_id=int(row["Book Id"]),
            rating=self._parse_rating(row.get("My Rating")),
            status=str(row.get("Exclusive Shelf", "")).strip(),
            date_read=self._parse_date(row.get("Date Read")),
            date_added=self._parse_date(row.get("Date Added")),
            shelves=self._parse_custom_shelves(row.get("Bookshelves")),
            read_count=int(row.get("Read Count", 0) or 0),
            review=self._optional_str(row.get("My Review")),
        )

        return book, reading

    # --------------------------------------------------
    # helpers privados
    # --------------------------------------------------

    def _optional_str(self, value) -> Optional[str]:
        if pd.isna(value) or str(value).strip() == "":
            return None
        return str(value).strip()

    def _optional_int(self, value) -> Optional[int]:
        try:
            v = int(float(value))
            return v if v > 0 else None
        except (TypeError, ValueError):
            return None

    def _clean_isbn(self, value) -> Optional[str]:
        """Goodreads exporta ISBN como =""0123456789"" — lo limpiamos."""
        if pd.isna(value):
            return None
        cleaned = re.sub(r'[=""]', "", str(value)).strip()
        return cleaned if cleaned else None

    def _parse_rating(self, value) -> Optional[int]:
        """0 significa sin rating en Goodreads → None."""
        try:
            r = int(float(value))
            return r if r > 0 else None
        except (TypeError, ValueError):
            return None

    def _parse_date(self, value) -> Optional[date]:
        if pd.isna(value) or str(value).strip() == "":
            return None
        try:
            return pd.to_datetime(value).date()
        except Exception:
            return None

    def _parse_custom_shelves(self, value) -> Optional[str]:
        """
        Devuelve solo las shelves custom (filtra 'read', 'to-read',
        'currently-reading' que son las de sistema).
        """
        system = {"read", "to-read", "currently-reading"}
        if pd.isna(value) or str(value).strip() == "":
            return None
        custom = [
            s.strip() for s in str(value).split(",") if s.strip().lower() not in system
        ]
        return ", ".join(custom) if custom else None
