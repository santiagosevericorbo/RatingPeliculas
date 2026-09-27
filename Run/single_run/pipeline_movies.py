from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from shared.duckdb_utils import get_connection
from shared.folder_runner import FolderRunner
from shared.python_runner import PythonRunner
from shared.sql_runner import SQLRunner
from shared.sqlserver_export import SQLServerExporter
from shared.export_config import EXPORT_TABLES

DB = ROOT / "db" / "movies.duckdb"
SCRIPTS = ROOT / "scripts"

PIPELINE = [
    "1_load/movies",
    "2_clean/movies",
    "2.5_map",
    "3_unique/movies",
    "4_filter/movies",
    "5_entity_resolution/movies",
    "6.5_enrichment",
    "6_master/movies",
    "7_score/movies",
    "8_user_activity/movies",
    "9_lists/movies",
]


def run_folder(folder_runner, sql_runner, folder):

    print()
    print("=" * 60)
    print(folder)
    print("=" * 60)

    for sql in folder_runner.sql_files_from(folder):
        sql_runner.run(sql)


def main():

    print()
    print("=" * 60)
    print("MOVIES PIPELINE")
    print("=" * 60)

    con = get_connection(DB)
    from shared.paths import LETTERBOXD_DIR, IMDB_DIR

    con.execute(f"""
    SET VARIABLE LB_DIR='{LETTERBOXD_DIR.as_posix()}';
    """)

    con.execute(f"""
    SET VARIABLE IMDB_DIR='{IMDB_DIR.as_posix()}';
    """)
    folder_runner = FolderRunner(SCRIPTS)
    sql_runner = SQLRunner(con)
    python_runner = PythonRunner(ROOT)

    #
    # Letterboxd
    #
    python_runner.run("imports/movies/lb/run_imports.py")

    #
    # SQL inicial
    #
    for folder in PIPELINE[:6]:
        run_folder(folder_runner, sql_runner, folder)

    #
    # Enriquecimiento
    #
    python_runner.run("imports/movies/tmdb/main.py")
    python_runner.run("imports/movies/torrentio/main.py")
    python_runner.run("imports/movies/metacritic/pipeline.py")

    #
    # SQL final
    #
    for folder in PIPELINE[6:]:
        run_folder(folder_runner, sql_runner, folder)

    #
    # Export SQL Server
    #
    print()
    print("=" * 60)
    print("EXPORTANDO A SQL SERVER")
    print("=" * 60)

    exporter = SQLServerExporter(con)
    exporter.export_tables(EXPORT_TABLES)

    con.close()

    print()
    print("=" * 60)
    print("PIPELINE FINALIZADO")
    print("=" * 60)


if __name__ == "__main__":
    main()
