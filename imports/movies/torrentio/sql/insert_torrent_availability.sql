INSERT INTO movie_torrent_availability
VALUES (?, ?, ?, ?, NOW())
ON CONFLICT (canonical_movie_id)
DO UPDATE SET
    best_seeders = EXCLUDED.best_seeders,
    quality = EXCLUDED.quality,
    retrieved_at = NOW();