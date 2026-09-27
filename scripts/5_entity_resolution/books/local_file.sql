-- =============================================================================
-- 5_entity_resolution/books/local_file.sql
-- Resuelve archivos locales (zlib) contra el catálogo de Goodreads.
--
-- Estrategia en cascada (orden de prioridad):
--   1. Match exacto por título normalizado
--   2. Match vía book_aliases (traducciones + variantes manuales enriquecidas)
--   3. Match fuzzy por Levenshtein cuando el autor también coincide (≥0.80 similitud)
--   4. Sin match → queda como unmatched para enriquecer aliases
-- =============================================================================

DROP TABLE IF EXISTS books_resolved;

CREATE TABLE books_resolved AS

WITH

-- Base: archivos locales parseados
local AS (
    SELECT
        id,
        file_name,
        parsed_title,
        parsed_author,
        parsed_title_norm,
        parsed_author_norm
    FROM book_local_file_parsed
    WHERE parsed_title_norm IS NOT NULL
      AND length(parsed_title_norm) > 2
),

-- Catálogo Goodreads normalizado
catalog AS (
    SELECT
        kraggle_id,
        title        AS canonical_title,
        author       AS canonical_author,
        title_clean  AS title_norm,
        author_clean AS author_norm
    FROM goodreads_books_unique
),

-- ── NIVEL 1: Match exacto título ────────────────────────────────────────────
exact_match AS (
    SELECT
        l.id,
        c.kraggle_id,
        c.canonical_title,
        c.canonical_author,
        'exact'    AS match_type,
        1.0        AS match_score
    FROM local l
    JOIN catalog c
        ON l.parsed_title_norm = c.title_norm
),

-- ── NIVEL 2: Match vía aliases ───────────────────────────────────────────────
-- book_aliases tiene: alias_title (normalizado), canonical_title (normalizado)
alias_match AS (
    SELECT
        l.id,
        c.kraggle_id,
        c.canonical_title,
        c.canonical_author,
        'alias'    AS match_type,
        0.95       AS match_score
    FROM local l
    -- el alias_title ya está normalizado igual que parsed_title_norm
    JOIN book_aliases a
        ON l.parsed_title_norm = a.alias_title
    JOIN catalog c
        ON a.canonical_title  = c.title_norm
    -- sólo para los que no matchearon exacto
    WHERE l.id NOT IN (SELECT id FROM exact_match)
),

-- ── NIVEL 3: Fuzzy match por Levenshtein (requiere autor coincidente) ────────
-- Bloqueamos por primera letra para evitar producto cartesiano completo
fuzzy_candidates AS (
    SELECT
        l.id,
        l.parsed_title_norm,
        l.parsed_author_norm,
        c.kraggle_id,
        c.canonical_title,
        c.canonical_author,
        c.title_norm    AS cat_title_norm,
        c.author_norm   AS cat_author_norm,

        (
            1.0 - (
                levenshtein(l.parsed_title_norm, c.title_norm)::DOUBLE
                / greatest(length(l.parsed_title_norm), length(c.title_norm))
            )
        ) AS title_sim,

        -- Similitud de autor (0 si alguno es nulo)
        CASE
            WHEN l.parsed_author_norm IS NOT NULL AND l.parsed_author_norm != ''
                 AND c.author_norm IS NOT NULL AND c.author_norm != ''
            THEN (
                1.0 - (
                    levenshtein(l.parsed_author_norm, c.author_norm)::DOUBLE
                    / greatest(length(l.parsed_author_norm), length(c.author_norm))
                )
            )
            ELSE 0.0
        END AS author_sim

    FROM local l
    JOIN catalog c
        ON left(l.parsed_title_norm, 2) = left(c.title_norm, 2)  -- blocking key

    -- Excluir ya resueltos
    WHERE l.id NOT IN (SELECT id FROM exact_match)
      AND l.id NOT IN (SELECT id FROM alias_match)
),

fuzzy_match AS (
    SELECT
        id,
        kraggle_id,
        canonical_title,
        canonical_author,
        'fuzzy'    AS match_type,
        title_sim  AS match_score

    FROM (
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY id
                ORDER BY (title_sim * 0.7 + author_sim * 0.3) DESC
            ) AS rn
        FROM fuzzy_candidates
        WHERE
            -- título muy similar sin importar autor
            title_sim >= 0.88
            OR
            -- título moderado + autor coincidente
            (title_sim >= 0.75 AND author_sim >= 0.70)
    )
    WHERE rn = 1
),

-- ── Combinar todos los niveles ───────────────────────────────────────────────
all_matches AS (
    SELECT * FROM exact_match
    UNION ALL
    SELECT * FROM alias_match
    UNION ALL
    SELECT * FROM fuzzy_match
),

-- Prioridad: exact > alias > fuzzy
ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY id
            ORDER BY
                CASE match_type
                    WHEN 'exact' THEN 1
                    WHEN 'alias' THEN 2
                    WHEN 'fuzzy' THEN 3
                END
        ) AS rn
    FROM all_matches
)

SELECT
    l.id,
    l.file_name,
    l.parsed_title,
    l.parsed_author,
    l.parsed_title_norm,
    l.parsed_author_norm,

    r.kraggle_id,
    r.canonical_title,
    r.canonical_author,
    r.match_type,
    round(r.match_score, 3)  AS match_score,

    CASE WHEN r.kraggle_id IS NOT NULL THEN 1 ELSE 0 END AS matched

FROM local l
LEFT JOIN ranked r
    ON l.id = r.id AND r.rn = 1;
