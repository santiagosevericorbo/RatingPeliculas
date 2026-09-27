CREATE OR REPLACE TABLE movie_metacritic AS

SELECT
    mmf.canonical_movie_id,
    mp.metascore,
    mp.user_score,
    mp.critic_review_count,
    mp.user_review_count

FROM movie_master_final mmf

LEFT JOIN metacritic_parsed mp
    USING(imdb_id)