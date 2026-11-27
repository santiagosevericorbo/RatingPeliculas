"""Consultas de películas disponibles en las tablas maestras DuckDB."""
class MovieRepository:
    QUERY = r"""
        SELECT m.canonical_movie_id, m.display_title AS title,
               r.ultimate_score AS weighted_score,
               i.genres AS genres,
               TRY_CAST(NULLIF(b.runtimeMinutes, '\N') AS INTEGER) AS duration_minutes,
               EXISTS (
                   SELECT 1 FROM global_user_activity a
                   WHERE a.title_norm = m.title_norm AND a.Year = m.year
                     AND a.source = 'watchlist'
               ) AS in_watchlist,
               EXISTS (
                   SELECT 1 FROM global_user_activity a
                   WHERE a.title_norm = m.title_norm AND a.Year = m.year
                     AND a.source IN ('watched', 'rated')
               ) AS is_watched,
               (
                   SELECT string_agg(DISTINCT a.platform, ', ' ORDER BY a.platform)
                   FROM global_user_activity a
                   WHERE a.title_norm = m.title_norm AND a.Year = m.year
                     AND a.source = 'watchlist'
               ) AS watchlist_sources
        FROM movie_master_final m
        LEFT JOIN final_ranking r ON r.title_norm = m.display_title
        LEFT JOIN imdb_movies_filtered i ON i.imdb_id = m.imdb_id
        LEFT JOIN imdb_basics b ON b.tconst = m.imdb_id
        ORDER BY r.ultimate_score DESC NULLS LAST, m.display_title
    """

    def __init__(self, connections):
        self.connections = connections

    def all_movies(self):
        with self.connections.connect(read_only=True) as connection:
            return connection.execute(self.QUERY).df().to_dict(orient="records")
