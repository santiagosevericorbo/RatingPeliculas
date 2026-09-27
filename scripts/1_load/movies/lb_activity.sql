-- =====================================================================
-- update_letterboxd_watchlist.sql
--
-- Actualiza SOLO la rama de Letterboxd (actividad vista + watchlist)
-- y recalcula todo lo que depende de ella hasta llegar a watchlist_ordered.
--
-- NO toca: IMDb, TMDb, libros, ni el dataset de ratings de Letterboxd
-- (letterboxd_movies_raw/clean/unique/filtered de Kaggle), que se asume
-- ya cargado en la base. Tampoco toca movie_streaming_availability ni
-- movie_torrent_availability_enriched (enrichment de streaming/torrents).
--
-- IMPORTANTE: revisá/actualizá esta ruta antes de correr el script si
-- exportaste un CSV nuevo de Letterboxd (la carpeta trae fecha):
--   data/movies/letterboxd/user-2026-07-05/watched_resolved.csv
--   data/movies/letterboxd/user-2026-07-05/watchlist_resolved.csv
--
-- Requiere que ya existan en la base (de una corrida anterior completa):
--   letterboxd_movies_clean, imdb_movies_filtered, tmdb_movies_filtered,
--   imdb_my_ratings_clean, imdb_watchlist_clean,
--   movie_streaming_availability, movie_torrent_availability_enriched
--
-- Uso (DuckDB CLI):
--   duckdb mi_base.duckdb -f update_letterboxd_watchlist.sql
-- =====================================================================

-- 1_load/movies/lb_activity.sql
--
-- Carga watched.csv / watchlist.csv (export crudo de Letterboxd, SIN
-- resolver) y calcula lb_slug en la misma consulta pegándole a la URL
-- de cada película y leyendo el header "Location" de la redirección
-- (letterboxd.com/<usuario>/film/<slug>/ -> letterboxd.com/film/<slug>/).
--
-- Reemplaza al paso Python (imports/movies/lb/run_imports.py) y a los
-- archivos intermedios watched_resolved.csv / watchlist_resolved.csv:
-- ya no hacen falta.

INSTALL http_request FROM community;
LOAD http_request;

-- Configuración del cliente HTTP:
--   - NO seguir el redirect automáticamente: nos interesa el header
--     "Location", no el contenido de la página final.
--   - Concurrencia baja para no golpear Letterboxd de más.
SET http_follow_redirects = false;
SET http_max_concurrency = 4;
SET http_timeout = 30;
SET http_retries = 3;

CREATE OR REPLACE TABLE letterboxd_watched_raw AS
SELECT
    *,
    regexp_extract(
        COALESCE(
            http_get("Letterboxd URI").headers['Location'],
            "Letterboxd URI"
        ),
        'film/([^/]+)/?$',
        1
    ) AS lb_slug
FROM read_csv_auto('C:/Users/Santiago/Documents/Documentos Personales/Ratings Peliculas/data/movies/letterboxd/user/watched.csv');

CREATE OR REPLACE TABLE letterboxd_watchlist_raw AS
SELECT
    *,
    regexp_extract(
        COALESCE(
            http_get("Letterboxd URI").headers['Location'],
            "Letterboxd URI"
        ),
        'film/([^/]+)/?$',
        1
    ) AS lb_slug
FROM read_csv_auto('C:/Users/Santiago/Documents/Documentos Personales/Ratings Peliculas/data/movies/letterboxd/user/watchlist.csv');

-- =========================
-- 2_clean: watched / watchlist
-- =========================
DROP TABLE IF EXISTS letterboxd_watched_clean;

CREATE TABLE letterboxd_watched_clean AS
SELECT
    lb_slug AS lb_slug,
    LOWER(TRIM(Name)) AS title_norm,
    date,
    CAST(year AS INT) AS year,
    CAST(
        NULLIF(
            regexp_extract(CAST(lb_slug AS VARCHAR), '(\d{4})$', 1),
            ''
        ) AS INT
    ) AS slug_year
FROM letterboxd_watched_raw;

DROP TABLE IF EXISTS letterboxd_watchlist_clean;

CREATE TABLE letterboxd_watchlist_clean AS
SELECT
    lb_slug AS lb_slug,
    LOWER(TRIM(Name)) AS title_norm,
    date,
    CAST(year AS INT) AS year,
    CAST(
        NULLIF(
            regexp_extract(CAST(lb_slug AS VARCHAR), '(\d{4})$', 1),
            ''
        ) AS INT
    ) AS slug_year
FROM letterboxd_watchlist_raw;


-- =========================
-- 2.5_map: mapeo de slugs <-> kaggle id
-- =========================
DROP TABLE IF EXISTS letterboxd_slug_candidates;

CREATE TABLE letterboxd_slug_candidates AS
SELECT
    w.lb_slug,
    m.lb_kaggle_id,
    w.title_norm,
    w.slug_year,
    m.year AS movie_year,
    ABS(m.year - w.year) AS year_diff
FROM letterboxd_watched_clean w
JOIN letterboxd_movies_clean m
    ON w.title_norm = m.title_norm
   AND ABS(m.year - w.year) <= 2;

DROP TABLE IF EXISTS letterboxd_slug_map;

CREATE TABLE letterboxd_slug_map AS
SELECT
    lb_slug,
    lb_kaggle_id,
    title_norm,
    movie_year AS year
FROM letterboxd_slug_candidates
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY lb_slug
    ORDER BY
        CASE WHEN year_diff = 0 THEN 0 ELSE 1 END,
        year_diff ASC,
        lb_kaggle_id
) = 1;

DROP TABLE IF EXISTS letterboxd_movies_mapped;

CREATE TABLE letterboxd_movies_mapped AS
SELECT
    COALESCE(m.lb_slug, CAST(c.lb_kaggle_id AS VARCHAR)) AS lb_id,
    c.title_norm,
    c.rating_letterboxd,
    c.minute,
    c.year,
    c.description,
    c.votes_letterboxd
FROM letterboxd_movies_clean c
LEFT JOIN letterboxd_slug_map m
    ON c.lb_kaggle_id = m.lb_kaggle_id;

DROP TABLE IF EXISTS letterboxd_watched_mapped;

CREATE TABLE letterboxd_watched_mapped AS
SELECT
    COALESCE(s.lb_slug, w.lb_slug) AS lb_id,
    w.title_norm,
    w.year,
    w.date
FROM letterboxd_watched_clean w
LEFT JOIN letterboxd_slug_map s
    ON w.lb_slug = s.lb_slug;

DROP TABLE IF EXISTS letterboxd_watchlist_mapped;

CREATE TABLE letterboxd_watchlist_mapped AS
SELECT
    COALESCE(s.lb_slug, w.lb_slug) AS lb_id,
    w.title_norm,
    w.year,
    w.date
FROM letterboxd_watchlist_clean w
LEFT JOIN letterboxd_slug_map s
    ON w.lb_slug = s.lb_slug;


-- =========================
-- 3_unique / 4_filter: películas letterboxd
-- =========================
DROP TABLE IF EXISTS letterboxd_movies_unique;
CREATE TABLE letterboxd_movies_unique AS
SELECT *
FROM (
    SELECT *,
           ROW_NUMBER() OVER(
               PARTITION BY title_norm, year
               ORDER BY votes_letterboxd DESC
           ) AS rn
    FROM letterboxd_movies_mapped
)
WHERE rn = 1;

DROP TABLE IF EXISTS letterboxd_movies_filtered;

CREATE TABLE letterboxd_movies_filtered AS
SELECT
    *
FROM letterboxd_movies_unique
WHERE
    rating_letterboxd >= 2.5
    ;


-- =========================
-- 5_entity_resolution: fusión con imdb/tmdb (sin recalcular esos dos)
-- =========================
DROP TABLE IF EXISTS all_sources;

CREATE TABLE all_sources AS

SELECT
    'imdb_' || imdb_id AS movie_id,
    title_norm,
    year,
    imdb_id,
    NULL AS tmdb_id,
    NULL AS lb_id,
    'imdb' AS source
FROM imdb_movies_filtered

UNION ALL

SELECT
    'tmdb_' || tmdb_id AS movie_id,
    title_norm,
    year,
    NULL AS imdb_id,
    tmdb_id,
    NULL AS lb_id,
    'tmdb' AS source
FROM tmdb_movies_filtered

UNION ALL

SELECT
    'lb_' || lb_id AS movie_id,
    title_norm,
    year,
    NULL AS imdb_id,
    NULL AS tmdb_id,
    lb_id,
    'letterboxd' AS source
FROM letterboxd_movies_filtered;


-- =========================
-- 6_master: master de películas
-- =========================
DROP TABLE IF EXISTS movie_master;

CREATE TABLE movie_master AS

SELECT
    COALESCE(i.title_norm,t.title_norm,l.title_norm) AS title_norm,
    COALESCE(i.year,t.year,l.year) AS year,

    i.imdb_id,
    t.tmdb_id,
    l.lb_id
FROM imdb_movies_filtered i

FULL OUTER JOIN tmdb_movies_filtered t
    ON i.title_norm = t.title_norm
   AND ABS(i.year - t.year) <= 1

FULL OUTER JOIN letterboxd_movies_filtered l
    ON COALESCE(i.title_norm,t.title_norm) = l.title_norm
   AND ABS(COALESCE(i.year,t.year) - l.year) <= 1;

DROP TABLE IF EXISTS movie_master_canonical;

CREATE TABLE movie_master_canonical AS
SELECT
    title_norm,
    year,
    MAX(imdb_id) AS imdb_id,
    MAX(tmdb_id) AS tmdb_id,
    MAX(lb_id) AS lb_id
FROM movie_master
GROUP BY title_norm, year;

DROP TABLE IF EXISTS movie_master_final;

CREATE TABLE movie_master_final AS
SELECT
    ROW_NUMBER() OVER (ORDER BY title_norm, year) AS canonical_movie_id,
    title_norm,
    year,
    title_norm || ' (' || year || ')' AS display_title,
    imdb_id,
    tmdb_id,
    lb_id
FROM movie_master_canonical;


-- =========================
-- 7_score: ranking híbrido
-- =========================
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
    FROM global_ratings;

DROP TABLE IF EXISTS popularity_score;

CREATE TABLE popularity_score AS

WITH base AS (
    SELECT * FROM nullified_global_ratings
),

log_votes AS (
    SELECT
        title_norm,
        LOG10(imdb_votes + 1) AS imdb_log,
        LOG10(tmdb_votes + 1) AS tmdb_log,
        LOG10(lb_votes + 1)   AS lb_log
    FROM base
),

normalized AS (
    SELECT
        title_norm,
        imdb_log / MAX(imdb_log) OVER() AS imdb_pop,
        tmdb_log / MAX(tmdb_log) OVER() AS tmdb_pop,
        lb_log   / NULLIF(MAX(lb_log)   OVER(), 0) AS lb_pop
    FROM log_votes
)

SELECT
    title_norm,
    (
        0.5 * COALESCE(imdb_pop,0) +
        0.3 * COALESCE(tmdb_pop,0) +
        0.2 * COALESCE(lb_pop,0)
    ) AS popularity_score
FROM normalized;

DROP TABLE IF EXISTS hybrid_ratings;

CREATE TABLE hybrid_ratings AS

WITH base AS (
    SELECT * FROM nullified_global_ratings
),

normalized AS (
    SELECT
        title_norm,

        imdb_rating,
        imdb_votes,

        (lb_rating_raw / 5.0) * 10 AS lb_rating,

        tmdb_rating,
        tmdb_votes

    FROM base
),

weights AS (
    SELECT
        title_norm,

        imdb_rating,
        lb_rating,
        tmdb_rating,

        CASE
            WHEN imdb_rating IS NOT NULL
            THEN imdb_votes / (imdb_votes + 25000.0)
        END AS w_imdb,

        CASE
            WHEN lb_rating IS NOT NULL
            THEN 0.8
        END AS w_lb,

        CASE
            WHEN tmdb_rating IS NOT NULL
            THEN tmdb_votes / (tmdb_votes + 10000.0)
        END AS w_tmdb

    FROM normalized
),

scored AS (
    SELECT
        title_norm,

        (
            imdb_rating * w_imdb +
            lb_rating * w_lb +
            tmdb_rating * w_tmdb
        )
        /
        NULLIF(
            w_imdb + w_lb + w_tmdb,
            0
        ) AS meta_score

    FROM weights
)

SELECT *
FROM scored
WHERE meta_score IS NOT NULL
ORDER BY meta_score DESC;

DROP TABLE IF EXISTS final_ranking;

CREATE TABLE final_ranking AS
SELECT
    h.title_norm,
    ROUND(h.meta_score,2) AS ranking_score,
    ROUND(p.popularity_score,2) AS popularity_score,
    ROUND((
        0.7 * h.meta_score +
        0.3 * (p.popularity_score * 10)
    ),2) AS ultimate_score

FROM hybrid_ratings h
JOIN popularity_score p USING(title_norm);


-- =========================
-- 8_user_activity: actividad global (imdb sin cambios + letterboxd actualizado)
-- =========================
DROP TABLE IF EXISTS imdb_user_activity;

CREATE TABLE imdb_user_activity AS
SELECT
    imdb_id AS id,
    title_norm || ' (' || year || ')' AS display_title,
    title_norm,
    year,
    'imdb' AS platform,
    'rated' AS source,
    "Your Rating" AS rating
FROM imdb_my_ratings_clean

UNION ALL

SELECT
    w.imdb_id AS id,
    w.title_norm || ' (' || w.year || ')' AS display_title,
    w.title_norm,
    w.year,
    'imdb' AS platform,
    'watchlist' AS source,
    NULL AS rating
FROM imdb_watchlist_clean w
LEFT JOIN imdb_my_ratings_clean r
    ON w.title_norm = r.title_norm
WHERE r.title_norm IS NULL;

DROP TABLE IF EXISTS letterboxd_user_activity;

CREATE TABLE letterboxd_user_activity AS

SELECT
    lb_id AS id,
    title_norm || ' (' || year || ')' AS display_title,
    title_norm,
    year,
    'letterboxd' AS platform,
    'watched' AS source,
    0 AS rating
FROM letterboxd_watched_mapped

UNION ALL

SELECT
    w.lb_id AS id,
    w.title_norm || ' (' || w.year || ')' AS display_title,
    w.title_norm,
    w.year,
    'letterboxd' AS platform,
    'watchlist' AS source,
    NULL AS rating
FROM letterboxd_watchlist_mapped w
LEFT JOIN letterboxd_watched_mapped r
    ON w.lb_id = r.lb_id
WHERE r.lb_id IS NULL;

DROP TABLE IF EXISTS global_user_activity;

CREATE TABLE global_user_activity AS
SELECT * FROM imdb_user_activity

UNION ALL

SELECT * FROM letterboxd_user_activity;

DROP TABLE IF EXISTS global_user_activity_watchlist;

CREATE TABLE global_user_activity_watchlist AS
SELECT * FROM global_user_activity
WHERE source = 'watchlist';

CREATE OR REPLACE TABLE global_user_activity_watchlist_unique AS
SELECT DISTINCT display_title as title_norm
FROM global_user_activity_watchlist
WHERE display_title IS NOT NULL;


-- =========================
-- 9_lists: watchlist final ordenada
-- =========================
CREATE OR REPLACE TABLE watchlist_ordered AS
SELECT
    f.*,
    CASE
        WHEN providers IS NULL THEN
            'Torrentio (' || COALESCE(best_seeders, 0) || ')'
        ELSE providers
    END AS providers_unificado
FROM final_ranking f
JOIN global_user_activity_watchlist_unique w
    ON f.title_norm = w.title_norm
LEFT JOIN movie_streaming_availability s
    ON f.title_norm = s.title_norm
LEFT JOIN movie_torrent_availability_enriched t
    ON f.title_norm = t.title_norm
ORDER BY ultimate_score DESC;

-- Fin. La tabla watchlist_ordered queda actualizada con la última
-- actividad y watchlist de Letterboxd.