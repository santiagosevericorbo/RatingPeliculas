DROP TABLE IF EXISTS all_sources;

CREATE TABLE all_sources AS

SELECT
    'imdb_' || imdb_id AS movie_id,
    title_norm,
    year,
    imdb_id,
    NULL AS tmdb_id,
    NULL AS lb_id,
    'imdb' AS source
FROM imdb_movies_filtered

UNION ALL

SELECT
    'tmdb_' || tmdb_id AS movie_id,
    title_norm,
    year,
    NULL AS imdb_id,
    tmdb_id,
    NULL AS lb_id,
    'tmdb' AS source
FROM tmdb_movies_filtered

UNION ALL

SELECT
    'lb_' || lb_id AS movie_id,
    title_norm,
    year,
    NULL AS imdb_id,
    NULL AS tmdb_id,
    lb_id,
    'letterboxd' AS source
FROM letterboxd_movies_filtered;