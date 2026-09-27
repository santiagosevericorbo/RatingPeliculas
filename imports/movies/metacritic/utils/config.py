from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = ROOT_DIR.parents[1]
DATA_DIR = PROJECT_DIR / "data"
HTML_DIR = DATA_DIR / "metacritic" / "html"
SQL_DIR = ROOT_DIR / "sql"
STEPS_DIR = ROOT_DIR / "steps"

HEADERS = {"User-Agent": "Mozilla/5.0"}
CHECKPOINT = DATA_DIR / "metacritic_slug_checkpoint.csv"
STEPS = [
    ("discover", STEPS_DIR / "1_discover.py"),
    ("fetch", STEPS_DIR / "2_fetch.py"),
    ("parse", STEPS_DIR / "3_parse.py"),
    ("load", STEPS_DIR / "4_load.py"),
]
SAVE_EVERY = 5000
REQUEST_SLEEP = 0.1
