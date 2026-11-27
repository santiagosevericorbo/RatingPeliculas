DROP TABLE IF EXISTS hybrid_ratings;

CREATE TABLE hybrid_ratings AS

WITH base AS (
    SELECT * FROM nullified_global_ratings
),

normalized AS (
    SELECT
        title_norm,

        imdb_rating,
        imdb_votes,

        (lb_rating_raw / 5.0) * 10 AS lb_rating,

        tmdb_rating,
        tmdb_votes,
        (movielens_rating_raw - 0.5) * (10.0 / 4.5) AS movielens_rating,
        movielens_votes

    FROM base
),

weights AS (
    SELECT
        title_norm,

        imdb_rating,
        lb_rating,
        tmdb_rating,
        movielens_rating,

        CASE 
            WHEN imdb_rating IS NOT NULL
            THEN imdb_votes / (imdb_votes + 25000.0)
        END AS w_imdb,

        CASE 
            WHEN lb_rating IS NOT NULL
            THEN 0.8
        END AS w_lb,

        CASE 
            WHEN tmdb_rating IS NOT NULL
            THEN tmdb_votes / (tmdb_votes + 10000.0)
        END AS w_tmdb,
        CASE
            WHEN movielens_rating IS NOT NULL
            THEN movielens_votes / (movielens_votes + 5000.0)
        END AS w_movielens

    FROM normalized
),

scored AS (
    SELECT
        title_norm,

        (
            imdb_rating * w_imdb +
            lb_rating * w_lb +
            tmdb_rating * w_tmdb
            + movielens_rating * w_movielens
        )
        /
        NULLIF(
            w_imdb + w_lb + w_tmdb + w_movielens,
            0
        ) AS meta_score

    FROM weights
)

SELECT *
FROM scored
WHERE meta_score IS NOT NULL
ORDER BY meta_score DESC;
