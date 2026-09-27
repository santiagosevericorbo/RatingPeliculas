from pathlib import Path

from shared.paths import PROJECT_ROOT, DATA_DIR, DB_DIR

# -------------------------------------------------------
# BASES DE DATOS
# -------------------------------------------------------
MOVIES_DB = DB_DIR / "movies.duckdb"
BOOKS_DB = DB_DIR / "books.duckdb"

# -------------------------------------------------------
# GOODREADS
# -------------------------------------------------------
GOODREADS_CSV = DATA_DIR / "goodreads" / "user" / "goodreads_library_export.csv"

# -------------------------------------------------------
# LETTERBOXD
# -------------------------------------------------------
LETTERBOXD_DIR = DATA_DIR / "letterboxd" / "user-2026-05-01"

LETTERBOXD_DATASETS = [
    {
        "input": LETTERBOXD_DIR / "watched.csv",
        "output": LETTERBOXD_DIR / "watched_resolved.csv",
        "uri_column": "Letterboxd URI",
    },
    {
        "input": LETTERBOXD_DIR / "watchlist.csv",
        "output": LETTERBOXD_DIR / "watchlist_resolved.csv",
        "uri_column": "Letterboxd URI",
    },
]

# -------------------------------------------------------
# LIBROS LOCALES
# Cambiá esta ruta a tu carpeta real de epubs/pdfs
# -------------------------------------------------------
BOOKS_ROOT = Path(
    r"C:\Users\Santiago\Documents\Documentos Personales\4- MISCELANIOUS\MISC\OCIO\1. KINDLE\SANTIAGO"
)
