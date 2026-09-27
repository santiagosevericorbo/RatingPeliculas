DROP TABLE IF EXISTS book_quality_score;

CREATE TABLE book_quality_score AS

WITH stats AS (

    SELECT
        AVG(average_rating) AS global_mean
    FROM books_base
),

base AS (

    SELECT
        b.title_norm,
        b.average_rating,
        b.ratings_count,

        s.global_mean

    FROM books_base b
    CROSS JOIN stats s
)

SELECT
    title_norm,

    (
        (
            ratings_count::DOUBLE
            /
            (ratings_count + 5000)
        ) * average_rating

        +

        (
            5000.0
            /
            (ratings_count + 5000)
        ) * global_mean

    ) AS quality_score

FROM base;