DROP TABLE IF EXISTS imdb_user_activity;

CREATE TABLE imdb_user_activity AS
SELECT
    imdb_id AS id,
    title_norm || ' (' || year || ')' AS display_title,
    title_norm,
    year,
    'imdb' AS platform,
    'rated' AS source,
    "Your Rating" AS rating
FROM imdb_my_ratings_clean

UNION ALL

SELECT
    w.imdb_id AS id,
    w.title_norm || ' (' || w.year || ')' AS display_title,
    w.title_norm,
    w.year,
    'imdb' AS platform,
    'watchlist' AS source,
    NULL AS rating
FROM imdb_watchlist_clean w
LEFT JOIN imdb_my_ratings_clean r
    ON w.title_norm = r.title_norm
WHERE r.title_norm IS NULL;