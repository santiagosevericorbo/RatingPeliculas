-- ============================================================
-- TEST: extracción de series en goodreads_activity_clean
-- Correr DESPUÉS de ejecutar gr_activity.sql
-- ============================================================


-- ------------------------------------------------------------
-- 1. TEST UNITARIO DE REGEX (sin depender de la tabla)
--    Esperado: todas las columnas "num" = '1', name sin coma
-- ------------------------------------------------------------

SELECT

    -- inline con punto y espacio
    regexp_extract(
        'vagabond, vol. 1',
        '(?:vol(?:ume)?[.]?|book|part)\s*([0-9]+)', 1
    ) AS vol_punto,               -- esperado: 1

    -- inline sin espacio entre punto y número
    regexp_extract(
        'pluto, vol.1',
        '(?:vol(?:ume)?[.]?|book|part)\s*([0-9]+)', 1
    ) AS vol_sin_espacio,         -- esperado: 1

    -- inline sin punto
    regexp_extract(
        'vagabond, vol 1',
        '(?:vol(?:ume)?[.]?|book|part)\s*([0-9]+)', 1
    ) AS vol_sin_punto,           -- esperado: 1

    -- inline volume
    regexp_extract(
        'vagabond, volume 1',
        '(?:vol(?:ume)?[.]?|book|part)\s*([0-9]+)', 1
    ) AS volume_num,              -- esperado: 1

    -- inline book
    regexp_extract(
        'some title, book 3',
        '(?:vol(?:ume)?[.]?|book|part)\s*([0-9]+)', 1
    ) AS book_num,                -- esperado: 3

    -- inline part
    regexp_extract(
        'some title, part 2',
        '(?:vol(?:ume)?[.]?|book|part)\s*([0-9]+)', 1
    ) AS part_num,                -- esperado: 2

    -- paréntesis: número entero
    regexp_extract(
        'dune (dune chronicles #1)',
        '\((?:[^)]+)\s*#([0-9]+(?:[.][0-9]+)?)\)', 1
    ) AS paren_num,               -- esperado: 1

    -- paréntesis: número decimal
    regexp_extract(
        'some novella (some series #1.5)',
        '\((?:[^)]+)\s*#([0-9]+(?:[.][0-9]+)?)\)', 1
    ) AS paren_num_decimal,       -- esperado: 1.5

    -- paréntesis: nombre SIN coma al final
    regexp_extract(
        'berserk, vol. 1 (berserk #1)',
        '\(([^,)]+?)\s*#[0-9]+(?:[.][0-9]+)?\)', 1
    ) AS paren_name,              -- esperado: berserk (sin coma)

    -- limpieza inline (con punto y espacio)
    trim(regexp_replace(
        'vagabond, vol. 1',
        '\s*,?\s*(?:vol(?:ume)?[.]?|book|part)\s*[0-9]+',
        '', 'ig'
    )) AS title_limpio_inline,    -- esperado: vagabond

    -- limpieza inline (sin espacio)
    trim(regexp_replace(
        'pluto, vol.1',
        '\s*,?\s*(?:vol(?:ume)?[.]?|book|part)\s*[0-9]+',
        '', 'ig'
    )) AS title_limpio_sin_esp,   -- esperado: pluto

    -- limpieza paréntesis
    trim(regexp_replace(
        'dune (dune chronicles #1)',
        '\s*\([^)]*#\d+[^)]*\)',
        ''
    )) AS title_limpio_paren;     -- esperado: dune


-- ------------------------------------------------------------
-- 2. TEST SOBRE LA TABLA: casos con volumen inline
--    Esperado: series_number poblado en todos
-- ------------------------------------------------------------

SELECT
    title,
    title_clean,
    series_name,
    series_number
FROM goodreads_activity_clean
WHERE
    lower(title) LIKE '%vol.%'
    OR lower(title) LIKE '%volume %'
    OR lower(title) LIKE '%, vol %'
ORDER BY title;


-- ------------------------------------------------------------
-- 3. TEST SOBRE LA TABLA: casos con serie en paréntesis
--    Esperado: series_name sin coma, series_number poblado
-- ------------------------------------------------------------

SELECT
    title,
    title_clean,
    series_name,
    series_number
FROM goodreads_activity_clean
WHERE title LIKE '%(% #%)'
ORDER BY series_name, NULLIF(series_number, '')::INTEGER;


-- ------------------------------------------------------------
-- 4. RESUMEN: filas con serie detectada vs sin serie
-- ------------------------------------------------------------

SELECT
    CASE
        WHEN series_number IS NOT NULL THEN 'con serie'
        ELSE 'sin serie'
    END AS tiene_serie,
    count(*) AS cantidad
FROM goodreads_activity_clean
GROUP BY 1
ORDER BY 1;


-- ------------------------------------------------------------
-- 5. SANITY CHECK: vagabond ordenado por volumen
-- ------------------------------------------------------------

SELECT
    title,
    title_clean,
    series_name,
    series_number
FROM goodreads_activity_clean
WHERE title_clean LIKE '%vagabond%'
ORDER BY NULLIF(series_number, '')::INTEGER;