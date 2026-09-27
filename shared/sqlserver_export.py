from time import perf_counter

import pandas as pd
from duckdb import DuckDBPyConnection

from shared.sqlserver_utils import (
    create_database_if_needed,
    sqlalchemy_engine,
)

DEFAULT_EXPORT_TABLES = [
    "movie_master_final",
    "watchlist_ordered",
    "global_user_activity",
    "global_user_activity_unique",
    "global_user_activity_watchlist",
    "global_user_activity_watchlist_unique",
    "movie_streaming_availability",
    "movie_torrent_availability_enriched",
    "streaming_availability",
    "final_ranking",
]


class SQLServerExporter:

    def __init__(self, duck_connection: DuckDBPyConnection):

        self.duck = duck_connection

        create_database_if_needed()

        self.engine = sqlalchemy_engine()

        self.tables = 0
        self.rows = 0

    def export_table(
        self,
        table_name: str,
        destination_table: str | None = None,
    ):
        if tables is None:
            tables = DEFAULT_EXPORT_TABLES
        if destination_table is None:
            destination_table = table_name

        start = perf_counter()

        print(f"\nExportando {table_name}...")

        df = self.duck.sql(f"""
            SELECT *
            FROM {table_name}
            """).df()

        df.to_sql(
            destination_table,
            self.engine,
            if_exists="replace",
            index=False,
        )

        elapsed = perf_counter() - start

        self.tables += 1
        self.rows += len(df)

        print(
            f"   ✔ {len(df):,} filas"
            f" ({len(df.columns)} columnas)"
            f" ({elapsed:.2f}s)"
        )

    def export_tables(self, tables):

        start = perf_counter()

        for table in tables:
            self.export_table(table)

        elapsed = perf_counter() - start

        print()
        print("=" * 60)
        print("SQL SERVER EXPORT")
        print("=" * 60)

        print(f"Tablas : {self.tables}")
        print(f"Filas  : {self.rows:,}")
        print(f"Tiempo : {elapsed:.2f}s")

        print("=" * 60)
