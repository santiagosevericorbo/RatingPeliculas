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
    FROM imdb_metrics_Rated
    ORDER BY weighted_rating DESC
)
TO '../exports/imdb_top_movies_Rated.csv'
WITH (HEADER, DELIMITER ',');