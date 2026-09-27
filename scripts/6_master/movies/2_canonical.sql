DROP TABLE IF EXISTS movie_master_canonical;

CREATE TABLE movie_master_canonical AS
SELECT
    title_norm,
    year,
    MAX(imdb_id) AS imdb_id,
    MAX(tmdb_id) AS tmdb_id,
    MAX(lb_id) AS lb_id
FROM movie_master
GROUP BY title_norm, year;