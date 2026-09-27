DROP TABLE IF EXISTS imdb_basics_clean;

CREATE TABLE imdb_basics_clean AS
SELECT
    tconst,
    titleType,
    LOWER(TRIM(primaryTitle)) AS title_norm,
    primaryTitle AS title_original,
    CAST(NULLIF(startYear, '\N') AS INTEGER) AS year,
    genres
FROM imdb_basics
WHERE
    startYear != '\\N';