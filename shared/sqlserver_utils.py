from urllib.parse import quote_plus

import pyodbc
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

SERVER = r"(localdb)\MSSQLLocalDB"
DATABASE = "movies"
DRIVER = "ODBC Driver 17 for SQL Server"


def master_connection() -> pyodbc.Connection:
    """
    Conexión a master.
    Se usa únicamente para crear la base de datos si no existe.
    """

    conn = pyodbc.connect(
        (
            f"DRIVER={{{DRIVER}}};"
            f"SERVER={SERVER};"
            "DATABASE=master;"
            "Trusted_Connection=yes;"
        ),
        autocommit=True,
    )

    return conn


def create_database_if_needed() -> None:
    """
    Crea la base movies únicamente si todavía no existe.
    """

    conn = master_connection()

    cursor = conn.cursor()

    cursor.execute(f"""
IF DB_ID('{DATABASE}') IS NULL
BEGIN
    CREATE DATABASE [{DATABASE}]
END
""")

    cursor.close()
    conn.close()


def sqlalchemy_engine() -> Engine:
    """
    Devuelve un Engine SQLAlchemy listo para usar.
    """

    params = quote_plus(
        (
            f"DRIVER={{{DRIVER}}};"
            f"SERVER={SERVER};"
            f"DATABASE={DATABASE};"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
    )

    return create_engine(
        f"mssql+pyodbc:///?odbc_connect={params}",
        fast_executemany=True,
        future=True,
    )


def test_connection() -> None:

    create_database_if_needed()

    engine = sqlalchemy_engine()

    with engine.begin() as conn:

        conn.execute(text("SELECT 1"))
