DROP TABLE IF EXISTS imdb_movies_unique;
CREATE TABLE imdb_movies_unique AS
SELECT *
FROM (
    SELECT *,
           ROW_NUMBER() OVER(
               PARTITION BY title_norm, year
               ORDER BY votes_imdb DESC
           ) AS rn
    FROM imdb_movies_clean
)
WHERE rn = 1;