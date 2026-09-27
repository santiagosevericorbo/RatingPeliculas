import duckdb
import subprocess
import platform

from .paths import DB_PATH

DB = str(DB_PATH)


def kill_duckdb_processes():

    if platform.system() == "Windows":
        subprocess.run(
            ["taskkill", "/F", "/IM", "duckdb.exe"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def get_connection():

    kill_duckdb_processes()

    return duckdb.connect(DB)
