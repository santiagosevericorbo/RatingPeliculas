-- =============================================================================
-- local_books_parse.sql
-- Parsea título y autor desde el nombre de archivo normalizado (zlib_downloads).
-- Maneja los patrones reales observados en los datos:
--   "Title (Author) (Z-Library)"
--   "Title by Author (z-lib.org)"
--   "Author Lastname - Title"
--   "Title_with_underscores_HASHCODE"
--   Archivos sin nombre útil (hashes numéricos)
-- =============================================================================

DROP TABLE IF EXISTS book_local_file_parsed;

CREATE TABLE book_local_file_parsed AS

WITH base AS (

    SELECT
        id,
        file_path,
        file_name,
        clean_name   -- viene de book_local_file_clean
    FROM book_local_file_clean

),

-- 1. Quitar ruido residual: hashes alfanuméricos al final, extensiones dobles, etc.
strip_noise AS (

    SELECT
        *,

        -- Quita hashes tipo "_ZNRLLZT4URWRYZVVH4G23TZYSCUW3OOI" al final
        regexp_replace(
            -- Quita extensiones residuales (.epub, .mobi) que quedaron en el stem
            regexp_replace(
                clean_name,
                '\.(epub|mobi|pdf|azw3?)(\s|$)',
                ' ',
                'ig'
            ),
            '_[A-Z0-9]{10,}$',
            ''
        ) AS s1

    FROM base

),

-- 2. Quitar marcas de descarga
strip_source AS (

    SELECT
        *,
        trim(
            regexp_replace(
                s1,
                '\(z-library\)|\(z-lib\.org\)|\(z-lib org\)|\(annas archive\)',
                '',
                'ig'
            )
        ) AS s2

    FROM strip_noise

),

-- 3. Detectar y clasificar el patrón del nombre
classify AS (

    SELECT
        *,

        CASE
            -- Patrón: "Title (Author Name)" — autor entre paréntesis al final
            WHEN regexp_matches(trim(s2), '^(.+?)\s*\(([^()]{4,})\)\s*$')
            THEN 'paren_author'

            -- Patrón: "Title by Author" — separado por " by "
            WHEN s2 ILIKE '% by %'
            THEN 'by_separator'

            -- Patrón: "Lastname Firstname - Title" — separado por " - "
            WHEN s2 LIKE '% - %'
            THEN 'dash_separator'

            -- Sin patrón claro: usar todo como título
            ELSE 'title_only'
        END AS pattern

    FROM strip_source

),

-- 4. Extraer título y autor según el patrón detectado
extract_parts AS (

    SELECT
        id,
        file_path,
        file_name,
        clean_name,
        s2 AS cleaned_stem,
        pattern,

        CASE pattern

            WHEN 'paren_author'
            THEN trim(
                    regexp_extract(trim(s2), '^(.+?)\s*\([^()]{4,}\)\s*$', 1)
                 )

            WHEN 'by_separator'
            -- Todo antes del primer " by " es el título
            THEN trim(
                    regexp_replace(s2, '\s+by\s+.+$', '', 'i')
                 )

            WHEN 'dash_separator'
            -- "Autor - Titulo": el título está DESPUÉS del guión
            -- Heurística: si la primera parte parece un nombre propio (pocas palabras),
            -- asumimos que es el autor. Si no, es parte del título.
            THEN CASE
                    WHEN length(split_part(s2, ' - ', 1)) < 30
                         AND array_length(string_split(trim(split_part(s2, ' - ', 1)), ' ')) <= 4
                    THEN trim(split_part(s2, ' - ', 2))
                    ELSE trim(s2)
                 END

            ELSE trim(s2)  -- title_only

        END AS parsed_title_raw,

        CASE pattern

            WHEN 'paren_author'
            THEN trim(
                    regexp_extract(trim(s2), '^.+?\s*\(([^()]{4,})\)\s*$', 1)
                 )

            WHEN 'by_separator'
            THEN trim(
                    regexp_replace(s2, '^.+?\s+by\s+', '', 'i')
                 )

            WHEN 'dash_separator'
            THEN CASE
                    WHEN length(split_part(s2, ' - ', 1)) < 30
                         AND array_length(string_split(trim(split_part(s2, ' - ', 1)), ' ')) <= 4
                    THEN trim(split_part(s2, ' - ', 1))
                    ELSE NULL
                 END

            ELSE NULL

        END AS parsed_author_raw

    FROM classify

),

-- 5. Normalizar título igual que el resto del pipeline:
--    lower → quitar acentos → quitar puntuación → colapsar espacios
normalize AS (

    SELECT
        *,

        trim(
            regexp_replace(
                regexp_replace(
                    replace(replace(replace(replace(replace(
                        lower(parsed_title_raw),
                    'á','a'),'é','e'),'í','i'),'ó','o'),'ú','u'),
                    '[^a-z0-9 ]', '', 'g'
                ),
                '\s+', ' ', 'g'
            )
        ) AS parsed_title_norm,

        trim(
            regexp_replace(
                regexp_replace(
                    replace(replace(replace(replace(replace(
                        lower(coalesce(parsed_author_raw, '')),
                    'á','a'),'é','e'),'í','i'),'ó','o'),'ú','u'),
                    '[^a-z0-9 ]', '', 'g'
                ),
                '\s+', ' ', 'g'
            )
        ) AS parsed_author_norm

    FROM extract_parts

)

SELECT
    id,
    file_path,
    file_name,
    clean_name,
    pattern,
    parsed_title_raw   AS parsed_title,
    parsed_author_raw  AS parsed_author,
    parsed_title_norm,
    parsed_author_norm

FROM normalize;
