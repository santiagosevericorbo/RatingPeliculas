from shared.paths import LETTERBOXD_DIR

DATASETS = [
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
