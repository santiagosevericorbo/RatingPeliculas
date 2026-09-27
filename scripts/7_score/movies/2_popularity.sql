DROP TABLE IF EXISTS popularity_score;

CREATE TABLE popularity_score AS

WITH base AS (
    SELECT * FROM nullified_global_ratings
),

log_votes AS (
    SELECT
        title_norm,
        LOG10(imdb_votes + 1) AS imdb_log,
        LOG10(tmdb_votes + 1) AS tmdb_log,
        LOG10(lb_votes + 1)   AS lb_log
    FROM base
),

normalized AS (
    SELECT
        title_norm,
        imdb_log / MAX(imdb_log) OVER() AS imdb_pop,
        tmdb_log / MAX(tmdb_log) OVER() AS tmdb_pop,
        lb_log   / NULLIF(MAX(lb_log)   OVER(), 0) AS lb_pop
    FROM log_votes
)

SELECT
    title_norm,
    (
        0.5 * COALESCE(imdb_pop,0) +
        0.3 * COALESCE(tmdb_pop,0) +
        0.2 * COALESCE(lb_pop,0)
    ) AS popularity_score
FROM normalized;