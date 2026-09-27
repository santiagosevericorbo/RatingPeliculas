DROP TABLE IF EXISTS tmdb_watch_providers_clean;

CREATE TABLE tmdb_watch_providers_clean AS
SELECT
    tmdb_id,
    provider_name
FROM tmdb_watch_providers;