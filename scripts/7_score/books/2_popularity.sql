DROP TABLE IF EXISTS book_popularity;

CREATE TABLE book_popularity AS

WITH base AS (

    SELECT
        title_norm,

        LOG10(COALESCE(ratings_count,0) + 1) AS ratings_log,
        LOG10(COALESCE(text_reviews_count,0) + 1) AS reviews_log

    FROM books_base
),

normalized AS (

    SELECT
        title_norm,

        ratings_log / MAX(ratings_log) OVER() AS ratings_pop,
        reviews_log / MAX(reviews_log) OVER() AS reviews_pop

    FROM base
)

SELECT
    title_norm,

    (
        0.8 * ratings_pop +
        0.2 * reviews_pop
    ) AS popularity_score

FROM normalized;