"""Ejecución secuencial de SQL configurable por JSON."""
from pathlib import Path
from .settings import Settings
from .database import DuckDBConnectionFactory


class SqlPipelineRunner:
    def __init__(self, settings: Settings, connections: DuckDBConnectionFactory):
        self.settings = settings
        self.connections = connections

    def run(self, selected_steps: list[int] | None = None) -> None:
        stage_config = self.settings.config["stages"]
        available = {stage["number"]: stage for stage in stage_config}
        selected = list(available) if selected_steps is None else selected_steps
        unknown = set(selected) - set(available)
        if unknown:
            raise ValueError(f"Etapas no configuradas: {sorted(unknown)}")

        with self.connections.connect() as connection:
            self._set_input_variables(connection)
            for number in selected:
                stage = available[number]
                if number == 0:
                    self._convert_letterboxd(connection)
                    continue
                for folder in stage["folders"]:
                    sql_files = sorted((self.settings.project_path("scripts") / folder).rglob("*.sql"))
                    if not sql_files:
                        raise FileNotFoundError(f"La etapa {number} no contiene SQL: {folder}")
                    for sql_file in sql_files:
                        print(f"[Etapa {number}] {sql_file.relative_to(self.settings.project_root)}")
                        sql = sql_file.read_text(encoding="utf-8")
                        sql = self._adapt_legacy_paths(sql)
                        connection.execute(sql)

    def _set_input_variables(self, connection) -> None:
        imdb_dir = self.settings.project_path(self.settings.config["imdb_directory"])
        candidates = sorted(imdb_dir.glob("user-*"))
        if candidates:
            imdb_dir = candidates[-1]
        escaped = imdb_dir.as_posix().replace("'", "''")
        connection.execute(f"SET VARIABLE IMDB_DIR = '{escaped}'")

    def _convert_letterboxd(self, connection) -> None:
        source = self.settings.project_path(self.settings.config["letterboxd_csv"])
        target = self.settings.project_path(self.settings.config["letterboxd_parquet"])
        if not source.exists():
            raise FileNotFoundError(f"No se encontró el CSV de Letterboxd: {source}")
        target.parent.mkdir(parents=True, exist_ok=True)
        src, dst = source.as_posix().replace("'", "''"), target.as_posix().replace("'", "''")
        print(f"[Etapa 0] CSV → Parquet: {source.relative_to(self.settings.project_root)}")
        connection.execute(f"COPY (SELECT * FROM read_csv_auto('{src}')) TO '{dst}' (FORMAT PARQUET)")

    def _adapt_legacy_paths(self, sql: str) -> str:
        old = "data/letterboxd/letterboxd_movies.parquet"
        target = self.settings.project_path(self.settings.config["letterboxd_parquet"]).as_posix()
        return sql.replace(old, target)
