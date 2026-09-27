-- =============================================================================
-- 5_entity_resolution/books/2_aliases.sql
-- Carga book_aliases.csv y genera una versión normalizada lista para JOINs.
--
-- El CSV tiene columnas: alias_title, canonical_title
-- Ambas ya están normalizadas (lowercase, sin acentos, sin puntuación)
-- porque enrich_aliases.py las escribe así.
-- =============================================================================

DROP TABLE IF EXISTS book_aliases;

CREATE TABLE book_aliases AS

WITH raw AS (

    SELECT *
    FROM read_csv(
        'data/books/manual/book_aliases.csv',
        header       = true,
        all_varchar  = true,
        null_padding = true
    )

),

-- Doble normalización defensiva: por si alguien editó el CSV a mano
normalized AS (

    SELECT

        trim(
            regexp_replace(
                regexp_replace(
                    replace(replace(replace(replace(replace(
                        lower(alias_title),
                    'á','a'),'é','e'),'í','i'),'ó','o'),'ú','u'),
                    '[^a-z0-9 ]', '', 'g'
                ),
                '\s+', ' ', 'g'
            )
        ) AS alias_title,

        trim(
            regexp_replace(
                regexp_replace(
                    replace(replace(replace(replace(replace(
                        lower(canonical_title),
                    'á','a'),'é','e'),'í','i'),'ó','o'),'ú','u'),
                    '[^a-z0-9 ]', '', 'g'
                ),
                '\s+', ' ', 'g'
            )
        ) AS canonical_title

    FROM raw
    WHERE alias_title IS NOT NULL
      AND canonical_title IS NOT NULL

)

SELECT DISTINCT
    alias_title,
    canonical_title
FROM normalized
-- Evitar que un alias apunte a sí mismo sin sentido
WHERE alias_title != canonical_title
   OR alias_title  = canonical_title;  -- (mantiene self-aliases para títulos ya canónicos)
