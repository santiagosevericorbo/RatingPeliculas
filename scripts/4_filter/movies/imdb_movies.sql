DROP TABLE IF EXISTS imdb_movies_filtered;

CREATE TABLE imdb_movies_filtered AS
SELECT
    *
FROM imdb_movies_unique
WHERE
    rating_imdb >= 5.0
    AND votes_imdb >= 10000;