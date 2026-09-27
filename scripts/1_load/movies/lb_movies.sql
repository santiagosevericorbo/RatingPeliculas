DROP TABLE IF EXISTS letterboxd_movies_raw;

CREATE TABLE letterboxd_movies_raw AS
SELECT *
-- FROM read_csv_auto('../data/letterboxd/letterboxd_movies.csv');
-- FROM read_csv_auto('data/letterboxd/letterboxd_movies.csv');
FROM read_parquet('data/letterboxd/letterboxd_movies.parquet');