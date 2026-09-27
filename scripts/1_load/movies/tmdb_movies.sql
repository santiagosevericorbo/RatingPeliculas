CREATE OR REPLACE TABLE tmdb_movies AS
SELECT *
FROM read_parquet('data/tmdb/tmdb_movies.parquet');