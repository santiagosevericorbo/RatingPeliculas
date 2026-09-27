DROP TABLE IF EXISTS final_book_ranking;

CREATE TABLE final_book_ranking AS

SELECT
    q.title_norm,

    ROUND(q.quality_score, 2) AS quality_score,

    ROUND(p.popularity_score, 2) AS popularity_score,

    ROUND(
        (
            0.75 * q.quality_score
        ) +
        (
            0.25 * (p.popularity_score * 5)
        ),
        2
    ) AS ultimate_score

FROM book_quality_score q
JOIN book_popularity p USING(title_norm)

ORDER BY ultimate_score DESC;