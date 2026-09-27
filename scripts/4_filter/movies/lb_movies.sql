DROP TABLE IF EXISTS letterboxd_movies_filtered;

CREATE TABLE letterboxd_movies_filtered AS
SELECT
    *
FROM letterboxd_movies_unique
WHERE
    rating_letterboxd >= 2.5
    ;