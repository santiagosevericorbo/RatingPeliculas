"""Factory de conexiones DuckDB."""
from contextlib import contextmanager
from pathlib import Path
import duckdb


class DuckDBConnectionFactory:
    def __init__(self, database_path: Path):
        self.database_path = database_path

    @contextmanager
    def connect(self, read_only: bool = False):
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = duckdb.connect(str(self.database_path), read_only=read_only)
        try:
            yield connection
        finally:
            connection.close()
