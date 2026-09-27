DROP TABLE IF EXISTS nullified_global_ratings;

CREATE TABLE nullified_global_ratings AS
    SELECT
        title_norm,
        NULLIF(rating_imdb, 0) AS imdb_rating,
        NULLIF(rating_letterboxd,0) AS lb_rating_raw,
        NULLIF(rating_tmdb,0) AS tmdb_rating,
        COALESCE(votes_imdb,0) AS imdb_votes,
        COALESCE(votes_tmdb,0) AS tmdb_votes,
        COALESCE(votes_letterboxd,0) AS lb_votes
    FROM global_ratings