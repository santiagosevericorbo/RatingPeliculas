COPY (
    SELECT *
    FROM read_csv_auto('data/letterboxd/letterboxd_movies.csv')
)
TO 'data/letterboxd/letterboxd_movies.parquet'
(FORMAT PARQUET);