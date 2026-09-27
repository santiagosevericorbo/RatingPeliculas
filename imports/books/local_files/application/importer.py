from pathlib import Path
from tqdm import tqdm

from application.scanner import LocalBookScanner
from application.matcher import GoodreadsMatcher
from infrastructure.repository import LocalFileRepository
from shared.console import success, info


class LocalFileImporter:

    def __init__(
        self,
        scanner: LocalBookScanner,
        matcher: GoodreadsMatcher,
        repository: LocalFileRepository,
    ):
        self.scanner = scanner
        self.matcher = matcher
        self.repository = repository

    def run(self) -> None:
        info(f"Escaneando {self.scanner.root}")
        books = list(self.scanner.scan())

        rows = []
        matched = 0

        for book in tqdm(
            books,
            desc="  → Importing local files",
            unit=" items",
            colour="cyan",
            dynamic_ncols=True,
        ):
            book.goodreads_id = self.matcher.match(book)
            if book.goodreads_id:
                matched += 1
            rows.append(self._to_tuple(book))

        self.repository.save(rows)
        success(
            f"{len(rows)} archivos importados ({matched} con match en Goodreads, {len(rows) - matched} sin match)"
        )

    def _to_tuple(self, b) -> tuple:

        return (
            b.file_path,
            b.file_name,
            b.raw_stem,
            b.normalized_stem,
            b.format,
            b.size_bytes,
        )
