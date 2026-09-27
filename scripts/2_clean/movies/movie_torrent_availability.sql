DROP TABLE IF EXISTS movie_torrent_availability_clean;

CREATE TABLE movie_torrent_availability_clean AS
SELECT
    canonical_movie_id,
    imdb_id,
    best_seeders
FROM movie_torrent_availability;