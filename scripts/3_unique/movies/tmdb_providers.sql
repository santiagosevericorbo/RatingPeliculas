DROP TABLE IF EXISTS tmdb_watch_providers_grouped;

CREATE TABLE tmdb_watch_providers_grouped AS
SELECT
    tmdb_id,
    STRING_AGG(DISTINCT provider_name, ' | ') AS providers
FROM tmdb_watch_providers_clean
GROUP BY tmdb_id;