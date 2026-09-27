DROP TABLE IF EXISTS movie_torrent_availability_enriched;

CREATE TABLE movie_torrent_availability_enriched AS
SELECT
    mmf.canonical_movie_id,
    mmf.display_title title_norm,
    p.best_seeders
FROM movie_torrent_availability_clean p
JOIN movie_master_final mmf
    ON mmf.imdb_id = p.imdb_id;