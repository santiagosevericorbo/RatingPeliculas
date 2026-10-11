"""Lee los créditos de dirección desde los datasets locales de IMDb, si están."""


class DirectorRepository:
    def __init__(self, connections, crew_path, names_path):
        self.connections = connections
        self.crew_path = crew_path
        self.names_path = names_path

    @property
    def available(self):
        return self.crew_path.is_file() and self.names_path.is_file()

    def for_imdb_ids(self, imdb_ids: list[str]) -> dict[str, list[str]]:
        if not imdb_ids or not self.available:
            return {}
        ids = ",".join("'" + value.replace("'", "''") + "'" for value in imdb_ids)
        crew = self.crew_path.as_posix().replace("'", "''")
        names = self.names_path.as_posix().replace("'", "''")
        query = f"""
            WITH selected_crew AS (
                SELECT tconst, directors
                FROM read_csv_auto('{crew}', delim='\\t', header=true)
                WHERE tconst IN ({ids})
            ), director_ids AS (
                SELECT tconst, unnest(string_split(directors, ',')) AS director_id
                FROM selected_crew
                WHERE directors IS NOT NULL AND directors <> '\\N'
            )
            SELECT d.tconst,
                   list(DISTINCT n.primaryName ORDER BY n.primaryName) AS directors
            FROM director_ids d
            JOIN read_csv_auto('{names}', delim='\\t', header=true) n
              ON n.nconst = d.director_id
            GROUP BY d.tconst
        """
        with self.connections.connect(read_only=True) as connection:
            rows = connection.execute(query).fetchall()
        return {imdb_id: directors for imdb_id, directors in rows}
