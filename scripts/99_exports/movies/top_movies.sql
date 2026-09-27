-- ======================================
-- EXPORT FINAL
-- ======================================

COPY (
    SELECT
        title,
        year,
        rating_imdb,
        votes_imdb,
        weighted_rating,
        genres
    FROM imdb_metrics
    ORDER BY weighted_rating DESC
)
TO '../exports/imdb_top_movies.csv'
WITH (HEADER, DELIMITER ',');