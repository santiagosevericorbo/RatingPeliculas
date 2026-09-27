DROP TABLE IF EXISTS letterboxd_slug_candidates;

CREATE TABLE letterboxd_slug_candidates AS
SELECT
    w.lb_slug,
    m.lb_kaggle_id,
    w.title_norm,
    w.slug_year,
    m.year AS movie_year,
    ABS(m.year - w.year) AS year_diff
FROM letterboxd_watched_clean w
JOIN letterboxd_movies_clean m
    ON w.title_norm = m.title_norm
   AND ABS(m.year - w.year) <= 2;