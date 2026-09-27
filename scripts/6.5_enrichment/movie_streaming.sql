DROP TABLE IF EXISTS movie_streaming_availability;

CREATE TABLE movie_streaming_availability AS
SELECT
    mmf.canonical_movie_id,
    mmf.display_title title_norm,
    p.providers
FROM tmdb_watch_providers_filtered p
JOIN movie_master_final mmf
    ON mmf.tmdb_id = p.tmdb_id;