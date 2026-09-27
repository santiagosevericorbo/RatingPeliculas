SELECT COUNT(*)
FROM global_activity_readlist_unique rl
JOIN final_book_ranking fr
    ON regexp_replace(rl.title_norm, '\s*\([0-9]{4}\)$', '')
     = regexp_replace(fr.title_norm, '\s*\([0-9]{4}\)$', '');