DROP TABLE IF EXISTS global_ratings;

CREATE TABLE global_ratings AS

SELECT
    
    m.display_title AS title_norm,
    m.year,

    i.rating_imdb,
    i.votes_imdb,

    l.rating_letterboxd,
    COALESCE(l.votes_letterboxd,0) AS votes_letterboxd,
    
    t.rating_tmdb,
    t.votes_tmdb,

    CASE 
        WHEN i.rating_imdb IS NOT NULL
         AND l.rating_letterboxd IS NOT NULL
         AND t.rating_tmdb IS NOT NULL
        THEN 1 ELSE 0
    END AS tieneRating,

    CASE 
        WHEN i.rating_imdb IS NOT NULL
         AND l.rating_letterboxd IS NOT NULL
        THEN 1 ELSE 0
    END AS tieneRatingSinScrapping

FROM movie_master_final m

LEFT JOIN imdb_movies_filtered i ON m.imdb_id = i.imdb_id

LEFT JOIN letterboxd_movies_filtered l ON m.title_norm = l.title_norm
   AND ABS(m.year - l.year) <= 1

LEFT JOIN tmdb_movies_filtered t ON m.tmdb_id = t.tmdb_id;