DROP TABLE IF EXISTS letterboxd_watched_mapped;

CREATE TABLE letterboxd_watched_mapped AS
SELECT
    COALESCE(s.lb_slug, w.lb_slug) AS lb_id,
    w.title_norm,
    w.year,
    w.date
FROM letterboxd_watched_clean w
LEFT JOIN letterboxd_slug_map s
    ON w.lb_slug = s.lb_slug;