CREATE OR REPLACE TABLE readlist_ordered AS
SELECT 
    fr.*
FROM final_book_ranking fr
JOIN global_activity_readlist_unique rl
    ON fr.title_norm = rl.title_norm
ORDER BY ultimate_score DESC;