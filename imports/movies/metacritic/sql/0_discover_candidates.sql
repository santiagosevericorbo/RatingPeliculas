SELECT
    mmf.imdb_id,
    mmf.title_norm,
    mmf.year,
    fr.popularity_score,
    fr.ultimate_score

FROM movie_master_final mmf

JOIN final_ranking fr
    USING(title_norm)

WHERE
    fr.popularity_score >= 0.15
    OR fr.ultimate_score >= 7


ORDER BY
    fr.popularity_score DESC