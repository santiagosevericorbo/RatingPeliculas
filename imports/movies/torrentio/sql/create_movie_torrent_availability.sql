CREATE TABLE IF NOT EXISTS movie_torrent_availability (
    canonical_movie_id INT,
    imdb_id TEXT,
    best_seeders INT,
    quality TEXT,
    retrieved_at TIMESTAMP,
    PRIMARY KEY (canonical_movie_id)
);