DROP TABLE IF EXISTS letterboxd_movies_mapped;

CREATE TABLE letterboxd_movies_mapped AS
SELECT
    COALESCE(m.lb_slug, CAST(c.lb_kaggle_id AS VARCHAR)) AS lb_id,
    c.title_norm,
    c.rating_letterboxd,
    c.minute,
    c.year,
    c.description,
    c.votes_letterboxd
FROM letterboxd_movies_clean c
LEFT JOIN letterboxd_slug_map m
    ON c.lb_kaggle_id = m.lb_kaggle_id;