DROP TABLE IF EXISTS movie_master_final;

CREATE TABLE movie_master_final AS
SELECT
    ROW_NUMBER() OVER (ORDER BY title_norm, year) AS canonical_movie_id,
    title_norm,
    year,
    title_norm || ' (' || year || ')' AS display_title,
    imdb_id,
    tmdb_id,
    lb_id
FROM movie_master_canonical;