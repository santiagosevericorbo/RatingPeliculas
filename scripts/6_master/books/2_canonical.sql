DROP TABLE IF EXISTS books_master_canonical;

CREATE TABLE books_master_canonical AS
SELECT *
FROM (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY title_norm, authors_norm
               ORDER BY ratings_count DESC NULLS LAST
           ) AS rn
    FROM books_master
)
WHERE rn = 1;