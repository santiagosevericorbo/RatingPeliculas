DROP TABLE IF EXISTS books_master;

CREATE TABLE books_master AS
SELECT
    title_norm,
    authors_norm,
    year,
    kraggle_id,
    isbn,
    ratings_count,
    text_reviews_count,
    average_rating
FROM goodreads_books_unique;