-- =============================================================================
-- 5_entity_resolution/books/1_candidates.sql
-- Detecta duplicados / variantes dentro de la actividad del usuario (goodreads).
--
-- También incluye una segunda query para linkear la actividad del usuario
-- con el catálogo de books.csv de Goodreads, resolviendo los títulos
-- que el usuario tiene en un idioma distinto al del catálogo.
-- =============================================================================


-- ── PARTE 1: duplicados dentro de goodreads_activity_clean ──────────────────

DROP TABLE IF EXISTS book_resolution_candidates;

CREATE TABLE book_resolution_candidates AS

WITH base AS (

    SELECT DISTINCT

        goodreads_id,
        title_clean,
        author_clean,
        year

    FROM goodreads_activity_clean

    WHERE title_clean IS NOT NULL
      AND length(title_clean) > 2

),

pairs AS (

    SELECT

        a.goodreads_id  AS id_a,
        b.goodreads_id  AS id_b,

        a.title_clean   AS title_a,
        b.title_clean   AS title_b,

        a.author_clean  AS author_a,
        b.author_clean  AS author_b,

        a.year          AS year_a,
        b.year          AS year_b

    FROM base a
    JOIN base b
        ON a.goodreads_id < b.goodreads_id
        -- Blocking: misma primera letra
       AND left(a.title_clean, 1) = left(b.title_clean, 1)

),

scored AS (

    SELECT

        *,

        (
            1.0 - (
                levenshtein(title_a, title_b)::DOUBLE
                / greatest(length(title_a), length(title_b))
            )
        ) AS title_similarity,

        (author_a = author_b) AS same_author,

        abs(
            coalesce(try_cast(year_a AS INTEGER), 0)
            - coalesce(try_cast(year_b AS INTEGER), 0)
        ) AS year_diff,

        (contains(title_a, title_b) OR contains(title_b, title_a)) AS title_contains

    FROM pairs

)

SELECT *
FROM scored
WHERE
    title_similarity >= 0.85
    OR (same_author AND title_similarity >= 0.70)
    OR (same_author AND title_contains)

ORDER BY same_author DESC, title_similarity DESC;


-- ── PARTE 2: linkeo actividad del usuario ↔ catálogo books.csv ──────────────
-- Resuelve los libros de la biblioteca del usuario que no tienen goodreads_id
-- en el catálogo, incluyendo libros en español que existen en inglés en el catálogo.

DROP TABLE IF EXISTS activity_catalog_link;

CREATE TABLE activity_catalog_link AS

WITH activity AS (

    SELECT DISTINCT
        goodreads_id,
        title,
        author,
        title_clean,
        author_clean,
        year
    FROM goodreads_activity_clean
    WHERE title_clean IS NOT NULL

),

catalog AS (

    SELECT
        kraggle_id,
        title        AS cat_title,
        author       AS cat_author,
        title_clean  AS cat_title_clean,
        author_clean AS cat_author_clean,
        isbn,
        ratings_count,
        average_rating
    FROM goodreads_books_unique

),

-- Nivel 1: match exacto por goodreads_id (el mejor caso)
by_id AS (

    SELECT
        a.goodreads_id,
        a.title,
        a.author,
        a.title_clean,
        a.author_clean,
        c.kraggle_id,
        c.cat_title,
        c.cat_author,
        c.isbn,
        c.ratings_count,
        c.average_rating,
        'id_match'  AS link_type,
        1.0         AS confidence
    FROM activity a
    JOIN catalog c
        ON a.goodreads_id = c.kraggle_id

),

-- Nivel 2: match por título exacto (cubre mismo idioma, mismo libro)
by_title AS (

    SELECT
        a.goodreads_id,
        a.title,
        a.author,
        a.title_clean,
        a.author_clean,
        c.kraggle_id,
        c.cat_title,
        c.cat_author,
        c.isbn,
        c.ratings_count,
        c.average_rating,
        'title_match' AS link_type,
        0.95          AS confidence
    FROM activity a
    JOIN catalog c
        ON a.title_clean = c.cat_title_clean
    WHERE a.goodreads_id NOT IN (SELECT goodreads_id FROM by_id)

),

-- Nivel 3: match vía aliases (traducciones / variantes)
by_alias AS (

    SELECT
        a.goodreads_id,
        a.title,
        a.author,
        a.title_clean,
        a.author_clean,
        c.kraggle_id,
        c.cat_title,
        c.cat_author,
        c.isbn,
        c.ratings_count,
        c.average_rating,
        'alias_match' AS link_type,
        0.90          AS confidence
    FROM activity a
    JOIN book_aliases al
        ON a.title_clean = al.alias_title
    JOIN catalog c
        ON al.canonical_title = c.cat_title_clean
    WHERE a.goodreads_id NOT IN (SELECT goodreads_id FROM by_id)
      AND a.goodreads_id NOT IN (SELECT goodreads_id FROM by_title)

),

all_links AS (
    SELECT * FROM by_id
    UNION ALL
    SELECT * FROM by_title
    UNION ALL
    SELECT * FROM by_alias
),

dedup AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY goodreads_id
            ORDER BY
                CASE link_type
                    WHEN 'id_match'    THEN 1
                    WHEN 'title_match' THEN 2
                    WHEN 'alias_match' THEN 3
                END
        ) AS rn
    FROM all_links
)

SELECT
    goodreads_id,
    title,
    author,
    title_clean,
    author_clean,
    kraggle_id,
    cat_title,
    cat_author,
    isbn,
    ratings_count,
    average_rating,
    link_type,
    confidence
FROM dedup
WHERE rn = 1;
