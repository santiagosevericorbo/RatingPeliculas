DROP TABLE IF EXISTS tmdb_movies_clean;

CREATE TABLE tmdb_movies_clean AS
SELECT
    tmdb_id,
    LOWER(TRIM(title)) AS title_norm,
    vote_average AS rating_tmdb,
    vote_count AS votes_tmdb,
    CASE WHEN release_date <> '' THEN year(cast(release_date AS DATE)) ELSE NULL END AS year

FROM tmdb_movies;