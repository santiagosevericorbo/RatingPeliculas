from pathlib import Path
from time import perf_counter

import duckdb


class SQLExecutor:
    """
    Ejecuta archivos SQL individuales sobre una conexión DuckDB.

    Responsabilidades:

        - leer el archivo
        - ejecutarlo
        - medir tiempos
        - mostrar progreso
        - devolver éxito/error

    No conoce nada del pipeline.
    """

    def __init__(
        self,
        connection: duckdb.DuckDBPyConnection,
        continue_on_error: bool = False,
    ):
        self.connection = connection
        self.continue_on_error = continue_on_error

        self.executed = 0
        self.failed = 0

    def execute_file(self, sql_file: Path):

        sql = sql_file.read_text(encoding="utf-8")

        print(f"\n▶ {sql_file.parent.name}/{sql_file.name}")

        start = perf_counter()

        try:

            self.connection.execute(sql)

            elapsed = perf_counter() - start

            self.executed += 1

            print(f"   ✔ OK ({elapsed:.2f}s)")

            return True

        except Exception as ex:

            elapsed = perf_counter() - start

            self.failed += 1

            print(f"   ✖ ERROR ({elapsed:.2f}s)")

            print()
            print(ex)
            print()

            if not self.continue_on_error:
                raise

            return False

    def execute_many(self, files):

        for file in files:
            self.execute_file(file)

    def summary(self):

        print()
        print("=" * 60)
        print("PIPELINE SUMMARY")
        print("=" * 60)

        print(f"SQL ejecutados : {self.executed}")
        print(f"Errores        : {self.failed}")

        print("=" * 60)
