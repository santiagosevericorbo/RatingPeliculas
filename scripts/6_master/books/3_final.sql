DROP TABLE IF EXISTS books_master_final;

CREATE TABLE books_master_final AS

WITH base AS (

    SELECT
        title_norm,

        LOWER(
            TRIM(
                SPLIT_PART(authors, ',', 1)
            )
        ) AS primary_author_norm,

        authors,
        year,
        kraggle_id,
        isbn,
        ratings_count,
        text_reviews_count,
        title_norm || ' (' || year || ')' AS display_title,
        average_rating

    FROM goodreads_books_clean
),

dedup AS (

    SELECT
        *,

        ROW_NUMBER() OVER (

            -- CAMBIO IMPORTANTE
            PARTITION BY title_norm

            ORDER BY
                ratings_count DESC NULLS LAST,
                text_reviews_count DESC NULLS LAST,
                average_rating DESC NULLS LAST,
                year DESC NULLS LAST

        ) AS rn

    FROM base
)

SELECT
    ROW_NUMBER() OVER (
        ORDER BY title_norm
    ) AS canonical_book_id,

    title_norm,
    primary_author_norm,
    authors,
    year,
    kraggle_id,
    isbn,
    ratings_count,
    text_reviews_count,
    average_rating,
    display_title

FROM dedup

WHERE rn = 1;