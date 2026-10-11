"""Interfaz de línea de comandos del ETL."""
import argparse
from pathlib import Path
from .application import MovieEtlApplication
from .settings import Settings

PACKAGE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = PACKAGE_DIR.parent


def create_application():
    return MovieEtlApplication(Settings.load(
        PROJECT_ROOT,
        PACKAGE_DIR / "config",
        PACKAGE_DIR / "movie_dashboard" / "public" / "data",
    ))


def main():
    parser = argparse.ArgumentParser(description="ETL modular de películas y publicación de JSON")
    parser.add_argument("--steps", nargs="+", type=int, help="Etapas SQL (0–9); por defecto, todas")
    parser.add_argument("--skip-etl", action="store_true", help="Publica desde las tablas DuckDB existentes")
    args = parser.parse_args()
    app = create_application()
    if not args.skip_etl:
        app.run_pipeline(args.steps)
    plan = app.publish_plan()
    history = app.publish_history()
    print(f"Publicadas {len(plan)} películas en movie_dashboard/public/data/monthly_movie_plan.json")
    print(f"Publicadas {len(history)} películas vistas en movie_dashboard/public/data/letterboxd_history.json")
    if not app.director_data_available:
        print("Directores pendientes: faltan title.crew.tsv.gz y name.basics.tsv.gz de IMDb en data/movies/imdb")


if __name__ == "__main__":
    main()
