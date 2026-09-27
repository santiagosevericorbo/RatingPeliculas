DROP TABLE IF EXISTS imdb_my_ratings_clean;

CREATE TABLE imdb_my_ratings_clean AS
SELECT
    Const AS imdb_id,
    year,
    LOWER(TRIM(Title)) AS title_norm,
    "Your Rating"
FROM imdb_my_ratings
