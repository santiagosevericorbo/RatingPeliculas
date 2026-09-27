DROP TABLE IF EXISTS goodreads_books_unique;
CREATE TABLE goodreads_books_unique AS
SELECT *
FROM (
    SELECT *,
           ROW_NUMBER() OVER(
               PARTITION BY title_norm, year
               ORDER BY ratings_count DESC
           ) AS rn
    FROM goodreads_books_clean
)
WHERE rn = 1;