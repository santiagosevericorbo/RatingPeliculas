# shared/paths.py

from pathlib import Path

# ------------------------------------------------------------------
# Proyecto
# ------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
DB_DIR = PROJECT_ROOT / "db"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

MOVIES_DB = DB_DIR / "movies.duckdb"
BOOKS_DB = DB_DIR / "books.duckdb"


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def latest_folder(base: Path, prefix: str = "user-") -> Path:
    """
    Devuelve la carpeta más reciente cuyo nombre comience con prefix.

    Ejemplo:
        user-2026-05-01
        user-2026-07-05
    -> devuelve user-2026-07-05
    """

    folders = [p for p in base.iterdir() if p.is_dir() and p.name.startswith(prefix)]

    if not folders:
        raise FileNotFoundError(f"No hay carpetas '{prefix}*' en {base}")

    return max(folders, key=lambda p: p.name)


# ------------------------------------------------------------------
# Movies
# ------------------------------------------------------------------

MOVIES_DATA = DATA_DIR / "movies"

LETTERBOXD_DIR = latest_folder(MOVIES_DATA / "letterboxd")
IMDB_DIR = latest_folder(MOVIES_DATA / "imdb")
