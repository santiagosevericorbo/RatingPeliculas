DROP TABLE IF EXISTS letterboxd_user_activity;

CREATE TABLE letterboxd_user_activity AS

SELECT
    lb_id AS id,
    title_norm || ' (' || year || ')' AS display_title,
    title_norm,
    year,
    'letterboxd' AS platform,
    'watched' AS source,
    0 AS rating
FROM letterboxd_watched_mapped

UNION ALL

SELECT
    w.lb_id AS id,
    w.title_norm || ' (' || w.year || ')' AS display_title,
    w.title_norm,
    w.year,
    'letterboxd' AS platform,
    'watchlist' AS source,
    NULL AS rating
FROM letterboxd_watchlist_mapped w
LEFT JOIN letterboxd_watched_mapped r
    ON w.lb_id = r.lb_id
WHERE r.lb_id IS NULL;