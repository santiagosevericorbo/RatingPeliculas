DROP TABLE IF EXISTS letterboxd_watchlist_mapped;

CREATE TABLE letterboxd_watchlist_mapped AS
SELECT
    COALESCE(s.lb_slug, w.lb_slug) AS lb_id,
    w.title_norm,
    w.year,
    w.date
FROM letterboxd_watchlist_clean w
LEFT JOIN letterboxd_slug_map s
    ON w.lb_slug = s.lb_slug;