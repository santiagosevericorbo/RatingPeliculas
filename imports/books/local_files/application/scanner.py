import re
import unicodedata
from pathlib import Path
from typing import Iterator

from domain.local_book import LocalBook
from shared.console import skip

SUPPORTED_FORMATS = {".epub", ".pdf", ".mobi", ".azw3", ".djvu"}


class LocalBookScanner:

    def __init__(self, root: Path):
        self.root = root

    def normalize_text(self, text: str) -> str:

        text = unicodedata.normalize("NFKD", text)
        text = text.encode("ascii", "ignore").decode("utf-8")

        return text

    def scan(self) -> Iterator[LocalBook]:

        for path in self.root.rglob("*"):

            if path.suffix.lower() not in SUPPORTED_FORMATS:
                continue

            try:
                yield self._to_local_book(path)

            except (FileNotFoundError, OSError) as e:
                skip(str(path), str(e), root=str(self.root))
                continue

    def _to_local_book(self, path: Path) -> LocalBook:

        raw_stem = path.stem

        normalized_stem = self.normalize_text(raw_stem)

        return LocalBook(
            file_path=str(path),
            file_name=path.name,
            raw_stem=raw_stem,
            normalized_stem=normalized_stem,
            format=path.suffix.lower().lstrip("."),
            size_bytes=path.stat().st_size,
        )
