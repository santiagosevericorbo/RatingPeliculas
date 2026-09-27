CREATE OR REPLACE TABLE imdb_my_ratings_raw AS
SELECT *
FROM read_csv_auto(getvariable('IMDB_DIR') || '/imdb_my_ratings.csv');

CREATE OR REPLACE TABLE imdb_watchlist_raw AS
SELECT *
FROM read_csv_auto(getvariable('IMDB_DIR') || '/imdb_watchlist.csv');