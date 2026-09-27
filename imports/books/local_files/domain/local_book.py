from dataclasses import dataclass


@dataclass
class LocalBook:

    file_path: str
    file_name: str

    raw_stem: str
    normalized_stem: str

    format: str
    size_bytes: int

    title_guess: str | None = None
    author_guess: str | None = None

    goodreads_id: int | None = None
