CREATE VIEW watchlist_with_fallback AS
SELECT
    w.*,
    t.best_seeders,
    CASE
        WHEN w.providers IS NOT NULL THEN 'streaming'
        WHEN t.best_seeders IS NOT NULL THEN 'torrent'
        ELSE 'unavailable'
    END AS availability
FROM watchlist_ordered w
LEFT JOIN movie_torrent_availability t
ON w.canonical_movie_id = t.canonical_movie_id;