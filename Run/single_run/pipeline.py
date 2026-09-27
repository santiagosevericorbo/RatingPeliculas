"""
pipeline_books.py
=================
Va en:  Run/single_run/pipeline_books.py
DB:     ../../books.db   (dos niveles arriba de Run/single_run/)
Scripts: ../../scripts/

Uso (desde cualquier lugar):
    python "Run/single_run/pipeline_books.py"
    python "Run/single_run/pipeline_books.py" --list
    python "Run/single_run/pipeline_books.py" --step "2_clean/gr_books"
    python "Run/single_run/pipeline_books.py" --skip-enrich
    python "Run/single_run/pipeline_books.py" --force-enrich
"""

import argparse
import platform
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import duckdb

# ── Paths: todo relativo a este archivo ──────────────────────────────────────
#
#   Run/single_run/pipeline_books.py   ← este archivo
#   Run/single_run/enrich_aliases.py   ← script de enriquecimiento
#   ../../                             ← raíz del proyecto
#   ../../books.db                     ← base de datos
#   ../../scripts/                     ← todos los SQL
#   ../../data/books/manual/           ← book_aliases.csv

HERE = Path(__file__).resolve().parent  # Run/single_run/
ROOT = HERE.parents[1]  # raíz del proyecto
SCRIPTS_DIR = ROOT / "scripts"
DB_PATH = ROOT / "books.db"
ALIASES_CSV = ROOT / "data" / "books" / "manual" / "book_aliases.csv"
ENRICH_PY = HERE / "enrich_aliases.py"

# ── Colores ANSI ──────────────────────────────────────────────────────────────

R = "\033[0m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YEL = "\033[33m"
RED = "\033[31m"
GRAY = "\033[90m"
BOLD = "\033[1m"


def hdr(msg):
    print(f"\n{BOLD}{CYAN}{'─'*60}\n  {msg}\n{'─'*60}{R}")


def ok(msg):
    print(f"{GREEN}  ✔  {msg}{R}")


def info(msg):
    print(f"{CYAN}  ℹ  {msg}{R}")


def warn(msg):
    print(f"{YEL}  ⚠  {msg}{R}")


def err(msg):
    print(f"{RED}  ✖  {msg}{R}")


def skip(msg):
    print(f"{GRAY}  ↷  {msg}{R}")


# ── Pasos del pipeline ────────────────────────────────────────────────────────
#   (label,  ruta_sql_relativa_a_scripts/)
#   (label,  None)  →  paso Python especial

STEPS = [
    # 1. Carga raw
    ("1_load / gr_books", "1_load/books/gr_books.sql"),
    ("1_load / gr_activity", "1_load/books/gr_activity.sql"),
    ("1_load / gr_read", "1_load/books/gr_read.sql"),
    ("1_load / gr_readList", "1_load/books/gr_readList.sql"),
    # 2. Limpieza
    ("2_clean / gr_books", "2_clean/books/gr_books.sql"),
    ("2_clean / gr_activity", "2_clean/books/gr_activity.sql"),
    ("2_clean / gr_read", "2_clean/books/gr_read.sql"),
    ("2_clean / gr_readList", "2_clean/books/gr_readList.sql"),
    ("2_clean / local_books", "2_clean/books/local_books.sql"),
    ("2_clean / local_books_parse", "2_clean/books/local_books_parse.sql"),
    # 3. Dedup catálogo
    ("3_unique / gr_books", "3_unique/books/gr_books.sql"),
    # 5a. Aliases (puede estar vacío en primera corrida)
    ("5_er / 2_aliases", "5_entity_resolution/books/2_aliases.sql"),
    # 5b. Candidates + cross-source link
    ("5_er / 1_candidates", "5_entity_resolution/books/1_candidates.sql"),
    # 5c. Resolver archivos locales contra catálogo
    ("5_er / local_file", "5_entity_resolution/books/local_file.sql"),
    # 4. Unmatched — insumo para enriquecimiento
    ("4_filter / unmatched", "4_filter/books/unmatched.sql"),
    # ENRIQUECIMIENTO (paso Python — consulta APIs)
    ("enrich / aliases [API]", None),
    # Re-correr entity resolution con aliases ya poblados
    ("5_er / 2_aliases [reload]", "5_entity_resolution/books/2_aliases.sql"),
    ("5_er / local_file [reload]", "5_entity_resolution/books/local_file.sql"),
    ("4_filter / unmatched [final]", "4_filter/books/unmatched.sql"),
    # 6. Master
    ("6_master / 1_raw", "6_master/books/1_raw.sql"),
    ("6_master / 2_canonical", "6_master/books/2_canonical.sql"),
    ("6_master / 3_final", "6_master/books/3_final.sql"),
    # 7. Score
    ("7_score / 1_base", "7_score/books/1_base.sql"),
    ("7_score / 2_popularity", "7_score/books/2_popularity.sql"),
    ("7_score / 3_quality", "7_score/books/3_quality.sql"),
    ("7_score / 4_ranking", "7_score/books/4_ranking.sql"),
    # 8. Actividad del usuario
    ("8_activity / 1_gr", "8_user_activity/books/1_gr.sql"),
    ("8_activity / 3_global", "8_user_activity/books/3_global.sql"),
    ("8_activity / 3_global_readlist", "8_user_activity/books/3_global_readlist.sql"),
    ("8_activity / 4_global_unique", "8_user_activity/books/4_global_unique.sql"),
    (
        "8_activity / 4_global_readlist_unique",
        "8_user_activity/books/4_global_readlist_unique.sql",
    ),
    # 9. Listas
    ("9_lists / readlist_ordered", "9_lists/books/readlist_ordered.sql"),
    # 99. Exports
    ("99_exports / zlib_downloads", "99_exports/books/zlib_downloads.sql"),
]

# ── DuckDB ────────────────────────────────────────────────────────────────────


def get_connection():
    if platform.system() == "Windows":
        subprocess.run(
            ["taskkill", "/F", "/IM", "duckdb.exe"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    return duckdb.connect(str(DB_PATH))


# ── Helpers ───────────────────────────────────────────────────────────────────


def init_aliases_csv():
    if not ALIASES_CSV.exists():
        ALIASES_CSV.parent.mkdir(parents=True, exist_ok=True)
        ALIASES_CSV.write_text("alias_title,canonical_title\n", encoding="utf-8")
        info(f"Creado {ALIASES_CSV.relative_to(ROOT)} (vacío)")


def run_sql(label, sql_path, con):
    sql = sql_path.read_text(encoding="utf-8")
    t0 = time.time()
    con.execute(sql)
    ok(f"{label}  {GRAY}({time.time() - t0:.1f}s){R}")


def run_enrich(force, con):
    if not ENRICH_PY.exists():
        warn(f"No encontré {ENRICH_PY.name} en {HERE} — saltando enriquecimiento")
        return con

    try:
        tables = {r[0] for r in con.execute("SHOW TABLES").fetchall()}
        if "books_unmatched" not in tables:
            warn("books_unmatched no existe — saltando enriquecimiento")
            return con
        pending = con.execute(
            "SELECT count(*) FROM books_unmatched "
            "WHERE unmatched_reason IN ('probable_spanish','probable_other_lang','unknown')"
        ).fetchone()[0]
    except Exception as e:
        warn(f"No se pudo consultar books_unmatched: {e}")
        return con

    if pending == 0 and not force:
        skip("enrich_aliases: sin pendientes")
        return con

    info(f"Enriqueciendo {pending} títulos sin match…")

    # Cerrar antes del subproceso — DuckDB no permite escritura concurrente
    con.close()

    result = subprocess.run(
        [sys.executable, str(ENRICH_PY)],
        cwd=str(ROOT),  # enrich_aliases.py espera correr desde la raíz
    )
    if result.returncode != 0:
        warn("enrich_aliases.py terminó con errores — continuando igual")
    else:
        ok("enrich_aliases completado")

    return get_connection()


def show_stats(con):
    try:
        rows = con.execute("SELECT * FROM books_match_stats").fetchall()
        print()
        info("Estadísticas de matching:")
        for match_type, total, pct in rows:
            bar = "█" * int(pct / 5)
            label = (match_type or "unmatched").ljust(14)
            print(f"    {CYAN}{label}{R}  {bar:<20}  {total:>5}  ({pct:.1f}%)")
    except Exception:
        pass


# ── Pipeline ──────────────────────────────────────────────────────────────────


def run_pipeline(only_step=None, skip_enrich=False, force_enrich=False):
    hdr("BOOKS PIPELINE")
    info(f"Root    : {ROOT}")
    info(f"DB      : {DB_PATH.relative_to(ROOT)}")
    info(f"Scripts : {SCRIPTS_DIR.relative_to(ROOT)}")
    info(f"Inicio  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    if not DB_PATH.exists():
        warn(f"La DB no existe todavía — se creará en {DB_PATH}")

    init_aliases_csv()
    con = get_connection()
    executed = 0
    errors = []

    try:
        for label, sql_rel in STEPS:

            if only_step and only_step not in label:
                continue

            if sql_rel is None:
                if skip_enrich:
                    skip(f"{label}  (--skip-enrich)")
                    continue
                con = run_enrich(force=force_enrich, con=con)
                executed += 1
                continue

            sql_path = SCRIPTS_DIR / sql_rel
            if not sql_path.exists():
                warn(f"No encontré: {sql_rel}")
                continue

            try:
                run_sql(label, sql_path, con)
                executed += 1
            except Exception as exc:
                err(f"{label}  →  {exc}")
                errors.append(label)
                resp = (
                    input(f"\n  {YEL}¿Continuar de todas formas? [s/N]{R} ")
                    .strip()
                    .lower()
                )
                if resp != "s":
                    err("Pipeline abortado.")
                    sys.exit(1)

    finally:
        show_stats(con)
        con.close()

    print()
    hdr("RESUMEN")
    ok(f"Pasos ejecutados : {executed}")
    if errors:
        warn(f"Con error        : {len(errors)}")
        for e in errors:
            print(f"    {RED}• {e}{R}")
    else:
        ok("Sin errores")
    info(f"Fin : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# ── CLI ───────────────────────────────────────────────────────────────────────


def main():
    p = argparse.ArgumentParser(description="Pipeline de libros")
    p.add_argument(
        "--step",
        metavar="NOMBRE",
        help="Ejecutar solo el paso cuyo label contenga NOMBRE",
    )
    p.add_argument(
        "--list", action="store_true", help="Listar todos los pasos sin ejecutar nada"
    )
    p.add_argument(
        "--skip-enrich",
        action="store_true",
        help="Saltar el paso de enriquecimiento de aliases",
    )
    p.add_argument(
        "--force-enrich",
        action="store_true",
        help="Forzar enriquecimiento aunque no haya pendientes",
    )
    args = p.parse_args()

    if args.list:
        hdr("PASOS DEL PIPELINE")
        for i, (label, sql_rel) in enumerate(STEPS, 1):
            kind = f"{GRAY}[python]{R}" if sql_rel is None else f"{GRAY}[sql]  {R}"
            print(f"  {i:>2}.  {kind}  {label}")
        return

    run_pipeline(
        only_step=args.step,
        skip_enrich=args.skip_enrich,
        force_enrich=args.force_enrich,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Interrumpido por el usuario.")
        sys.exit(0)
