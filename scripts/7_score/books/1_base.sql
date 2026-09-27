DROP TABLE IF EXISTS books_base;

CREATE TABLE books_base AS
SELECT
    kraggle_id,
    display_title as title_norm,
    authors,

    average_rating,
    ratings_count,
    text_reviews_count,

    year
FROM books_master_final;