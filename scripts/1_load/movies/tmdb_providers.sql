CREATE OR REPLACE TABLE tmdb_watch_providers AS
SELECT *
FROM read_parquet('data/tmdb/tmdb_watch_providers.parquet');