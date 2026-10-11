"""Datos de vistas del usuario en Letterboxd y calificaciones personales."""


class LetterboxdHistoryRepository:
    def __init__(self, connections, ratings_path):
        self.connections = connections
        self.ratings_path = ratings_path

    def watched_movies(self):
        ratings_cte = ""
        if self.ratings_path.is_file():
            path = self.ratings_path.as_posix().replace("'", "''")
            ratings_cte = f""",
                user_ratings AS (
                    SELECT LOWER(TRIM(Name)) AS title_norm,
                           TRY_CAST(Year AS INTEGER) AS year,
                           MAX(TRY_CAST(Rating AS DOUBLE) * 2) AS personal_rating
                    FROM read_csv_auto('{path}', header=true)
                    WHERE Rating IS NOT NULL
                    GROUP BY 1, 2
                )
            """
            rating_join = "LEFT JOIN user_ratings ur ON ur.title_norm = m.title_norm AND ur.year = m.year"
            personal_rating = "ur.personal_rating"
        else:
            rating_join = ""
            personal_rating = "NULL::DOUBLE AS personal_rating"

        query = f"""
            WITH watched AS (
                SELECT DISTINCT title_norm, Year AS year
                FROM global_user_activity
                WHERE platform = 'letterboxd' AND source = 'watched'
            )
            {ratings_cte}
            SELECT m.canonical_movie_id AS id, m.display_title AS title,
                   m.year, m.imdb_id,
                   i.genres,
                   r.ultimate_score AS weighted_score,
                   {personal_rating}
            FROM watched w
            JOIN movie_master_final m ON m.title_norm = w.title_norm AND m.year = w.year
            LEFT JOIN imdb_movies_filtered i ON i.imdb_id = m.imdb_id
            LEFT JOIN final_ranking r ON r.title_norm = m.display_title
            {rating_join}
            ORDER BY m.year, m.display_title
        """
        with self.connections.connect(read_only=True) as connection:
            return connection.execute(query).df().to_dict(orient="records")
