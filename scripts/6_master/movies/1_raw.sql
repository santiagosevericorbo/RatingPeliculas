DROP TABLE IF EXISTS movie_master;

CREATE TABLE movie_master AS

SELECT
    COALESCE(i.title_norm,t.title_norm,l.title_norm) AS title_norm,
    COALESCE(i.year,t.year,l.year) AS year,
    
    i.imdb_id,
    t.tmdb_id,
    l.lb_id
FROM imdb_movies_filtered i

FULL OUTER JOIN tmdb_movies_filtered t
    ON i.title_norm = t.title_norm
   AND ABS(i.year - t.year) <= 1

FULL OUTER JOIN letterboxd_movies_filtered l
    ON COALESCE(i.title_norm,t.title_norm) = l.title_norm
   AND ABS(COALESCE(i.year,t.year) - l.year) <= 1;