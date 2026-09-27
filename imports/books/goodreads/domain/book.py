from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Book:
    goodreads_id: int
    title: str
    author: str
    additional_authors: Optional[str]
    isbn: Optional[str]
    isbn13: Optional[str]
    publisher: Optional[str]
    binding: Optional[str]
    pages: Optional[int]
    year_published: Optional[int]
    year_original: Optional[int]


@dataclass
class BookReading:
    goodreads_id: int
    rating: Optional[int]       # None si es 0 (sin rating)
    status: str                  # read / to-read / currently-reading
    date_read: Optional[date]
    date_added: Optional[date]
    shelves: Optional[str]       # custom shelves (ej: "psichology")
    read_count: int
    review: Optional[str]
