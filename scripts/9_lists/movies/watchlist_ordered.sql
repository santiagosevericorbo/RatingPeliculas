CREATE OR REPLACE TABLE watchlist_ordered AS
SELECT 
    f.*,    
    CASE 
        WHEN providers IS NULL THEN 
            'Torrentio (' || COALESCE(best_seeders, 0) || ')'
        ELSE providers
    END AS providers_unificado
FROM final_ranking f
JOIN global_user_activity_watchlist_unique w
    ON f.title_norm = w.title_norm
LEFT JOIN movie_streaming_availability s
    ON f.title_norm = s.title_norm
LEFT JOIN movie_torrent_availability_enriched t
    ON f.title_norm = t.title_norm
ORDER BY ultimate_score DESC;