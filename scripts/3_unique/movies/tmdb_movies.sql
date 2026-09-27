DROP TABLE IF EXISTS tmdb_movies_unique;
CREATE TABLE tmdb_movies_unique AS
SELECT *
FROM (
    SELECT *,
           ROW_NUMBER() OVER(
               PARTITION BY title_norm, year
               ORDER BY votes_tmdb DESC
           ) AS rn
    FROM tmdb_movies_clean
)
WHERE rn = 1;