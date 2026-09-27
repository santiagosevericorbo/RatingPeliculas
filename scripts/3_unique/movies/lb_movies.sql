DROP TABLE IF EXISTS letterboxd_movies_unique;
CREATE TABLE letterboxd_movies_unique AS
SELECT *
FROM (
    SELECT *,
           ROW_NUMBER() OVER(
               PARTITION BY title_norm, year
               ORDER BY votes_letterboxd DESC
           ) AS rn
    FROM letterboxd_movies_mapped
)
WHERE rn = 1;