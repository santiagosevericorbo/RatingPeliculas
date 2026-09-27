DROP TABLE IF EXISTS final_ranking;

CREATE TABLE final_ranking AS
SELECT
    h.title_norm,
    ROUND(h.meta_score,2) AS ranking_score,
    ROUND(p.popularity_score,2) AS popularity_score,
    ROUND((
        0.7 * h.meta_score +
        0.3 * (p.popularity_score * 10)
    ),2) AS ultimate_score

FROM hybrid_ratings h
JOIN popularity_score p USING(title_norm);