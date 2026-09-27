DROP TABLE IF EXISTS tmdb_movies_filtered;

CREATE TABLE tmdb_movies_filtered AS
SELECT
    *
FROM tmdb_movies_unique
WHERE
    rating_tmdb >= 5
    ;