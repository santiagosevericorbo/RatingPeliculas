"""
enrich_aliases.py
=================
Lee los libros sin match (books_unmatched) desde DuckDB,
consulta Open Library y Google Books para encontrar el título
canónico en inglés, y genera/actualiza book_aliases.csv.

Uso:
    python imports/books/enrich_aliases.py

Requisitos:
    pip install duckdb requests

El script es idempotente: si book_aliases.csv ya existe,
lo lee primero y sólo enriquece los títulos que aún no tienen alias.
"""

import csv
import json
import os
import re
import sys
import time
import unicodedata
from pathlib import Path

import duckdb
import requests

# ── Configuración ─────────────────────────────────────────────────────────────

DB_PATH      = Path("db/books.duckdb")
ALIASES_PATH = Path("data/books/manual/book_aliases.csv")

# Cuántos segundos esperar entre llamadas a la API (respetar rate limits)
API_DELAY = 0.4

# Umbrales de confianza para aceptar un resultado automático
MIN_TITLE_SIM  = 0.60   # similitud mínima entre título buscado y resultado
MIN_AUTHOR_SIM = 0.50   # si tenemos autor, también lo verificamos

# ── Helpers de normalización (igual que el pipeline SQL) ─────────────────────

def normalize(text: str) -> str:
    """Lowercase + quitar acentos + quitar puntuación + colapsar espacios."""
    if not text:
        return ""
    text = text.lower()
    text = "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )
    text = re.sub(r"[^a-z0-9 ]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def levenshtein(a: str, b: str) -> int:
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            curr.append(min(prev[j] + 1, curr[j - 1] + 1,
                            prev[j - 1] + (ca != cb)))
        prev = curr
    return prev[-1]


def title_similarity(a: str, b: str) -> float:
    a, b = normalize(a), normalize(b)
    if not a or not b:
        return 0.0
    dist = levenshtein(a, b)
    return 1.0 - dist / max(len(a), len(b))


# ── Clientes de API ───────────────────────────────────────────────────────────

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "BookAliasEnricher/1.0 (personal project)"})


def _ol_search(title: str, author: str | None = None) -> list[dict]:
    """Open Library /search.json"""
    params = {
        "q": f"{title} {author or ''}".strip(),
        "fields": "title,author_name,key,language",
        "limit": 5,
    }
    try:
        r = SESSION.get("https://openlibrary.org/search.json",
                        params=params, timeout=10)
        r.raise_for_status()
        return r.json().get("docs", [])
    except Exception as exc:
        print(f"    [OL error] {exc}", file=sys.stderr)
        return []


def _gb_search(title: str, author: str | None = None) -> list[dict]:
    """Google Books volumes API (no key needed, 1000 req/day)"""
    q = f'intitle:"{title}"'
    if author:
        q += f' inauthor:"{author}"'
    params = {"q": q, "maxResults": 5, "langRestrict": "en", "printType": "books"}
    try:
        r = SESSION.get("https://www.googleapis.com/books/v1/volumes",
                        params=params, timeout=10)
        r.raise_for_status()
        items = r.json().get("items", [])
        return [i["volumeInfo"] for i in items]
    except Exception as exc:
        print(f"    [GB error] {exc}", file=sys.stderr)
        return []


def find_canonical_title(title_norm: str,
                         author_norm: str | None) -> tuple[str | None, str, float]:
    """
    Busca el título canónico en inglés.
    Devuelve: (canonical_title_norm, source, confidence)
    canonical_title_norm es None si no se encontró nada confiable.
    """
    best_title: str | None = None
    best_score: float = 0.0
    best_source: str = ""

    # ── Open Library ─────────────────────────────────────────────────────────
    ol_docs = _ol_search(title_norm, author_norm)
    time.sleep(API_DELAY)

    for doc in ol_docs:
        candidate = doc.get("title", "")
        sim = title_similarity(title_norm, candidate)

        # Bonus si el autor también coincide
        if author_norm:
            ol_authors = [normalize(a) for a in doc.get("author_name", [])]
            if any(title_similarity(author_norm, a) >= MIN_AUTHOR_SIM
                   for a in ol_authors):
                sim = min(1.0, sim + 0.10)

        if sim > best_score:
            best_score = sim
            best_title = normalize(candidate)
            best_source = "openlibrary"

    # ── Google Books (fallback o segunda opinión) ─────────────────────────────
    if best_score < MIN_TITLE_SIM:
        gb_items = _gb_search(title_norm, author_norm)
        time.sleep(API_DELAY)

        for item in gb_items:
            candidate = item.get("title", "")
            sim = title_similarity(title_norm, candidate)

            if author_norm:
                gb_authors = [normalize(a) for a in item.get("authors", [])]
                if any(title_similarity(author_norm, a) >= MIN_AUTHOR_SIM
                       for a in gb_authors):
                    sim = min(1.0, sim + 0.10)

            if sim > best_score:
                best_score = sim
                best_title = normalize(candidate)
                best_source = "googlebooks"

    if best_score >= MIN_TITLE_SIM and best_title and best_title != title_norm:
        return best_title, best_source, round(best_score, 3)

    return None, best_source, round(best_score, 3)


# ── I/O de aliases ────────────────────────────────────────────────────────────

def load_existing_aliases(path: Path) -> dict[str, str]:
    """Lee book_aliases.csv y devuelve {alias_title: canonical_title}."""
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["alias_title"]: row["canonical_title"] for row in reader}


def save_aliases(path: Path, aliases: dict[str, str]) -> None:
    """Escribe todos los aliases a CSV (sobrescribe)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(aliases.items(), key=lambda x: x[0])
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["alias_title", "canonical_title"])
        writer.writeheader()
        for alias, canonical in rows:
            writer.writerow({"alias_title": alias, "canonical_title": canonical})


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    if not DB_PATH.exists():
        sys.exit(f"No encontré la base de datos en {DB_PATH}")

    con = duckdb.connect(str(DB_PATH), read_only=True)

    # Verificar que books_unmatched existe
    tables = {r[0] for r in con.execute("SHOW TABLES").fetchall()}
    if "books_unmatched" not in tables:
        sys.exit("Tabla 'books_unmatched' no encontrada. "
                 "Ejecutá primero 4_filter/books/unmatched.sql")

    rows = con.execute("""
        SELECT parsed_title_norm, parsed_author_norm, unmatched_reason
        FROM books_unmatched
        WHERE unmatched_reason IN ('probable_spanish', 'probable_other_lang', 'unknown')
        ORDER BY unmatched_reason, parsed_title_norm
    """).fetchall()

    con.close()

    if not rows:
        print("No hay títulos sin match para enriquecer.")
        return

    aliases = load_existing_aliases(ALIASES_PATH)
    already = set(aliases.keys())

    to_process = [
        (title_norm, author_norm, reason)
        for title_norm, author_norm, reason in rows
        if title_norm not in already
    ]

    print(f"Títulos a enriquecer: {len(to_process)} "
          f"(ya resueltos: {len(already)})\n")

    new_count    = 0
    skip_count   = 0
    manual_count = 0
    manual_queue: list[dict] = []

    for i, (title_norm, author_norm, reason) in enumerate(to_process, 1):
        print(f"[{i}/{len(to_process)}] {title_norm!r}"
              + (f" / {author_norm!r}" if author_norm else ""))

        canonical, source, score = find_canonical_title(title_norm, author_norm)

        if canonical and canonical != title_norm:
            print(f"    ✓ [{source}] {canonical!r}  (sim={score})")
            aliases[title_norm] = canonical
            new_count += 1
        elif canonical == title_norm:
            # El título ya está en inglés canónico → apuntar a sí mismo
            print(f"    = ya parece canónico  (sim={score})")
            aliases[title_norm] = title_norm
            skip_count += 1
        else:
            print(f"    ✗ sin resultado confiable (sim={score}) → requiere revisión manual")
            manual_queue.append({
                "alias_title":     title_norm,
                "parsed_author":   author_norm or "",
                "unmatched_reason": reason,
                "best_score":      score,
            })
            manual_count += 1

        # Guardar progreso cada 20 entradas (por si se interrumpe)
        if i % 20 == 0:
            save_aliases(ALIASES_PATH, aliases)
            print(f"    [checkpoint] {i} procesados, {new_count} nuevos aliases guardados")

    # Guardar final
    save_aliases(ALIASES_PATH, aliases)

    # Exportar los que requieren revisión manual
    if manual_queue:
        manual_path = ALIASES_PATH.parent / "book_aliases_manual_review.csv"
        with manual_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["alias_title", "parsed_author",
                            "unmatched_reason", "best_score"]
            )
            writer.writeheader()
            writer.writerows(manual_queue)
        print(f"\n→ {manual_count} títulos para revisión manual guardados en: {manual_path}")

    print(f"\n{'─'*50}")
    print(f"Nuevos aliases agregados : {new_count}")
    print(f"Ya eran canónicos        : {skip_count}")
    print(f"Revisión manual pendiente: {manual_count}")
    print(f"Total en book_aliases.csv: {len(aliases)}")
    print(f"Archivo guardado en      : {ALIASES_PATH}")


if __name__ == "__main__":
    main()
