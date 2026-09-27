
SELECT
    w.title_norm,
    m.canonical_movie_id,
    m.imdb_id,
    w.ultimate_score,
    w.providers
FROM watchlist_ordered w
JOIN movie_master_final m
    ON w.title_norm = m.display_title
WHERE w.providers IS NULL;