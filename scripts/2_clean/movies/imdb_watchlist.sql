DROP TABLE IF EXISTS imdb_watchlist_clean;

CREATE TABLE imdb_watchlist_clean AS

SELECT
    Const as imdb_id,
    year,
    LOWER(TRIM(Title)) AS title_norm
FROM imdb_watchlist