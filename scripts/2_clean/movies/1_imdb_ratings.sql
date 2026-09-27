DROP TABLE IF EXISTS imdb_ratings_clean;

CREATE TABLE imdb_ratings_clean AS
SELECT
    tconst AS tconst,
    averageRating AS rating_imdb,
    numVotes AS votes_imdb
FROM imdb_ratings
WHERE
    numVotes IS NOT NULL;