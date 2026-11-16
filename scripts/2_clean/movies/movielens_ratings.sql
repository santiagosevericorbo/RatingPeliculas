DROP TABLE IF EXISTS movielens_movies_clean;
CREATE TABLE movielens_movies_clean AS
SELECT
    CAST(l.movieId AS BIGINT) AS movielens_id,
    CAST(l.imdbId AS BIGINT) AS imdb_numeric_id,
    CAST(l.tmdbId AS BIGINT) AS tmdb_id,
    m.title AS title_original,
    LOWER(TRIM(REGEXP_REPLACE(m.title, ' \\([0-9]{4}\\)$', ''))) AS title_norm,
    TRY_CAST(REGEXP_EXTRACT(m.title, '\\(([0-9]{4})\\)$', 1) AS INTEGER) AS year,
    AVG(TRY_CAST(r.rating AS DOUBLE)) AS rating_movielens,
    COUNT(*) AS votes_movielens
FROM movielens_links_raw l
JOIN movielens_movies_raw m ON CAST(l.movieId AS BIGINT) = CAST(m.movieId AS BIGINT)
JOIN movielens_ratings_raw r ON CAST(l.movieId AS BIGINT) = CAST(r.movieId AS BIGINT)
WHERE TRY_CAST(l.imdbId AS BIGINT) > 0
GROUP BY l.movieId, l.imdbId, l.tmdbId, m.title;
