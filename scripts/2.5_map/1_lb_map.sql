DROP TABLE IF EXISTS letterboxd_slug_map;

CREATE TABLE letterboxd_slug_map AS
SELECT
    lb_slug,
    lb_kaggle_id,
    title_norm,
    movie_year AS year
FROM letterboxd_slug_candidates
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY lb_slug
    ORDER BY
        CASE WHEN year_diff = 0 THEN 0 ELSE 1 END,
        year_diff ASC,
        lb_kaggle_id
) = 1;