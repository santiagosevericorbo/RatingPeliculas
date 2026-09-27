-- =============================================================================
-- 4_filter/books/unmatched.sql
-- Genera la tabla de archivos locales sin match en el catálogo Goodreads.
-- Esta tabla es el insumo para el script Python de enriquecimiento automático
-- (imports/books/enrich_aliases.py) que consulta Open Library / Google Books
-- y genera book_aliases.csv con las traducciones al inglés canónico.
-- =============================================================================

DROP TABLE IF EXISTS books_unmatched;

CREATE TABLE books_unmatched AS

SELECT
    br.id,
    br.file_name,
    br.parsed_title,
    br.parsed_author,
    br.parsed_title_norm,
    br.parsed_author_norm,

    -- Razón probable de no-match (útil para priorizar la corrección manual)
    CASE
        -- Detectar títulos probablemente en español
        WHEN regexp_matches(
            br.parsed_title_norm,
            '\b(el|la|los|las|un|una|unos|unas|de|del|en|y|por|para|con|que|es|su)\b'
        )
        THEN 'probable_spanish'

        -- Detectar otros idiomas romances comunes
        WHEN regexp_matches(
            br.parsed_title_norm,
            '\b(les|des|une|le|la|il|di|della|del|los|das|die|der)\b'
        )
        THEN 'probable_other_lang'

        -- Título muy corto (puede ser hash o abreviación)
        WHEN length(br.parsed_title_norm) < 5
        THEN 'too_short'

        -- Título tiene números que parecen código
        WHEN regexp_matches(br.parsed_title_norm, '^\d+')
        THEN 'numeric_id'

        ELSE 'unknown'
    END AS unmatched_reason

FROM books_resolved br
WHERE br.matched = 0
  AND length(br.parsed_title_norm) > 3  -- descartar hashes sin sentido

ORDER BY
    -- Primero los que probablemente son idioma distinto (candidatos a alias)
    CASE unmatched_reason
        WHEN 'probable_spanish'    THEN 1
        WHEN 'probable_other_lang' THEN 2
        WHEN 'unknown'             THEN 3
        ELSE 4
    END,
    br.parsed_title_norm;


-- Vista rápida de estadísticas de matching
CREATE OR REPLACE VIEW books_match_stats AS

SELECT
    match_type,
    count(*)                          AS total,
    round(count(*) * 100.0
          / sum(count(*)) OVER(), 1)  AS pct
FROM books_resolved
GROUP BY match_type

UNION ALL

SELECT
    'TOTAL'  AS match_type,
    count(*) AS total,
    100.0    AS pct
FROM books_resolved

ORDER BY
    CASE match_type
        WHEN 'exact' THEN 1
        WHEN 'alias' THEN 2
        WHEN 'fuzzy' THEN 3
        WHEN 'TOTAL' THEN 5
        ELSE 4
    END;
