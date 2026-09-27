from pathlib import Path


def load_sql(sql_dir: Path, name: str) -> str:
    """
    Carga un archivo .sql desde sql_dir.
    Cada módulo pasa su propio SQL_DIR → sin acoplamiento a paths globales.
    """
    return (sql_dir / name).read_text(encoding="utf-8")
