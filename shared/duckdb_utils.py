import duckdb
import subprocess
import platform
from pathlib import Path


def _kill_duckdb_processes() -> None:
    """Mata procesos duckdb.exe en Windows para liberar el lock del archivo."""
    if platform.system() == "Windows":
        subprocess.run(
            ["taskkill", "/F", "/IM", "duckdb.exe"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def get_connection(db_path: Path) -> duckdb.DuckDBPyConnection:
    """
    Retorna una conexión DuckDB al archivo indicado.
    Recibe el path explícitamente → cada módulo decide a qué DB conectarse.
    """
    _kill_duckdb_processes()
    return duckdb.connect(str(db_path))
