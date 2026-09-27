CREATE OR REPLACE TABLE missing_movies AS
SELECT f.*
FROM final_ranking f
LEFT JOIN global_user_activity_unique m
    ON f.title_norm = m.title_norm
WHERE m.title_norm IS NULL
ORDER BY ultimate_score DESC;