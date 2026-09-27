CREATE OR REPLACE TABLE streaming_availability AS
SELECT f.*,w.providers
FROM final_ranking f
JOIN movie_streaming_availability w
    ON f.title_norm = w.title_norm
ORDER BY ultimate_score DESC;