DROP TABLE IF EXISTS letterboxd_watched_clean;

CREATE TABLE letterboxd_watched_clean AS
SELECT
    lb_slug AS lb_slug,
    LOWER(TRIM(Name)) AS title_norm,
    date,
    CAST(year AS INT) AS year,
    CAST(
        NULLIF(
            regexp_extract(CAST(lb_slug AS VARCHAR), '(\\d{4})$', 1),
            ''
        ) AS INT
    ) AS slug_year
FROM letterboxd_watched_raw;