DROP TABLE IF EXISTS letterboxd_movies_clean;

CREATE TABLE letterboxd_movies_clean AS
SELECT
    id AS lb_kaggle_id,
    LOWER(TRIM(name)) AS title_norm,
    rating as rating_letterboxd,
    minute,
    CAST(date AS INTEGER) AS year,
    description,
    NULL AS votes_letterboxd
FROM letterboxd_raw
WHERE name IS NOT NULL
    AND rating IS NOT NULL;