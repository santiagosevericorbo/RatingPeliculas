SELECT COUNT(*)
FROM final_book_ranking fr
JOIN global_activity_readlist_unique rl
    ON fr.title_norm = rl.title_norm;