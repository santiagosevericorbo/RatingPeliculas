DROP TABLE IF EXISTS imdb_movies_clean;

CREATE TABLE imdb_movies_clean AS
SELECT
    b.titleType AS title_type,
    b.tconst AS imdb_id,
    b.title_original,
    b.title_norm,
    b.year,
    r.rating_imdb,
    r.votes_imdb,
    b.genres
FROM imdb_basics_clean b
JOIN imdb_ratings_clean r
    ON b.tconst = r.tconst
WHERE
    r.votes_imdb >= 0
    AND b.titleType IN ('movie', 'tvMovie','short');