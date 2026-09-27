DROP TABLE IF EXISTS tmdb_watch_providers_filtered;

CREATE TABLE tmdb_watch_providers_filtered AS
SELECT *
FROM tmdb_watch_providers_grouped
WHERE
    providers ILIKE '%Netflix%'
    OR providers ILIKE '%HBO Max%'
    OR providers ILIKE '%Disney Plus%';