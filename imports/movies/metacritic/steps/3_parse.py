from bs4 import BeautifulSoup
from pathlib import Path
import re
import sys
from tqdm import tqdm

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))
from utils.sql_utils import load_sql
from utils.config import (
    HTML_DIR,
    DATA_DIR,
    SQL_DIR,
    HEADERS,
    SAVE_EVERY,
)

from imports.movies.metacritic.utils.duckdb_utils import get_connection

query_parse = load_sql("3_parse.sql")


def extract_score(text):
    if not text:
        return None
    m = re.search(r"\d+(\.\d+)?", text)
    return float(m.group()) if m else None


def extract_int(text):
    if not text:
        return None
    m = re.search(r"\d[\d,]*", text)
    return int(m.group().replace(",", "")) if m else None


def parse_file(path):

    html = path.read_text(encoding="utf-8")

    # sanity check
    if "metacritic" not in html.lower():
        return None, None

    soup = BeautifulSoup(html, "html.parser")

    critic = soup.select_one('[data-testid="critic-score"]')
    user = soup.select_one('[data-testid="user-score"]')
    critic_count_el = soup.select_one('[data-testid="critic-reviews-count"]')
    user_count_el = soup.select_one('[data-testid="user-reviews-count"]')

    critic_review_count = extract_int(critic_count_el.text if critic_count_el else None)

    user_review_count = extract_int(user_count_el.text if user_count_el else None)
    metascore = extract_score(critic.text if critic else None)
    userscore = extract_score(user.text if user else None)

    return metascore, userscore, critic_review_count, user_review_count


def main():

    con = get_connection()

    files = list(HTML_DIR.glob("*.html"))
    print(f"Archivos a parsear: {len(files)}")

    con.execute(query_parse)

    buffer = []

    for i, file in enumerate(tqdm(files, desc="Parsing Metacritic")):

        imdb_id = file.stem

        metascore, userscore, critic_review_count, user_review_count = parse_file(file)

        buffer.append(
            (
                imdb_id,
                metascore,
                userscore,
                critic_review_count,
                user_review_count,
            )
        )

        if len(buffer) >= SAVE_EVERY:
            con.executemany(
                "INSERT INTO metacritic_parsed VALUES (?, ?, ?, ?, ?)", buffer
            )
            buffer.clear()

    # flush final
    if buffer:
        con.executemany("INSERT INTO metacritic_parsed VALUES (?, ?, ?, ?, ?)", buffer)

    con.close()


if __name__ == "__main__":
    main()
