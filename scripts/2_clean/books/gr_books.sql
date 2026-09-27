DROP TABLE IF EXISTS goodreads_books_clean;

CREATE TABLE goodreads_books_clean AS

WITH base AS (

    SELECT

        bookid as kraggle_id,

        title,
        authors AS author,

        lower(title)  AS title_lc,
        lower(authors) AS author_lc,

        isbn,
        num_pages pages,
        ratings_count,
        average_rating,
        text_reviews_count,
        YEAR(TRY_STRPTIME(publication_date, '%m/%d/%Y')) AS year_original

    FROM goodreads_books_raw

),

clean_ascii AS (

    SELECT

        *,

        replace(replace(replace(replace(replace(
            title_lc,
            'á','a'),
            'é','e'),
            'í','i'),
            'ó','o'),
            'ú','u'
        ) AS title_ascii,

        replace(replace(replace(replace(replace(
            author_lc,
            'á','a'),
            'é','e'),
            'í','i'),
            'ó','o'),
            'ú','u'
        ) AS author_ascii

    FROM base

),
extract_series AS (

    SELECT

        *,

        -- Extrae nombre de serie desde paréntesis: "Title (Series Name #3)"
        -- [^,)]+ excluye la coma para no capturar "berserk,"
        -- Captura todo hasta el # y luego limpia coma/espacios finales
        trim(
            regexp_replace(
                regexp_extract(
                    title_ascii,
                    '\(([^)]+)\s*#[0-9]+(?:[.][0-9]+)?\)',
                    1
                ),
                '[,\s]+$', ''
            )
        ) AS series_name_paren,

        -- Extrae número de serie desde paréntesis: "#3" o "#1.5"
        -- DESPUÉS
        regexp_extract(
            title_ascii,
            '\((?:[^)]+)\s*#([0-9]+(?:[.][0-9]+)?)(?:-[0-9]+)?\)',
            1
        ) AS series_number_paren,
        -- Extrae número romano inline desde el título original (mayúsculas)
        regexp_extract(
            title,
            '(?i)(?:vol(?:ume)?[.]?|book|part)\s+([IVXLCDMivxlcdm]+)',
            1
        ) AS series_number_roman,
        -- Extrae número inline: "vol. 1", "vol.1", "vol 1", "volume 2", "book 3", "part 4"
        -- \s* (cero o más espacios) para cubrir "Vol.1" sin espacio
        regexp_extract(
            title_ascii,
            '(?:vol(?:ume)?[.]?|book|part)\s*([0-9]+)',
            1
        ) AS series_number_inline

    FROM clean_ascii

),

merge_series AS (

    SELECT

        *,

        series_name_paren AS series_name,

        coalesce(
            nullif(series_number_paren, ''),
            nullif(series_number_inline, ''),
            nullif(series_number_roman, '')
        ) AS series_number

    FROM extract_series

),

remove_series_info AS (

    SELECT

        *,

        regexp_replace(
            regexp_replace(
                title_ascii,
                '\s*\([^)]#\d+(?:-\d+)?[^)]\)',
                ''
            ),
            '\s*,?\s*(?:vol(?:ume)?[.]?|book|part)\s*(?:[0-9]+|[ivxlcdm]+)',
            '',
            'ig'
        ) AS title_no_series

    FROM merge_series

),

remove_subtitles AS (

    SELECT

        *,

        regexp_replace(
            title_no_series,
            '[:\-].*$',
            ''
        ) AS title_no_subtitle

    FROM remove_series_info

),

normalize AS (

    SELECT

        *,

        regexp_replace(
            title_no_subtitle,
            '[^a-z0-9 ]',
            '',
            'g'
        ) AS normalized_title,

        regexp_replace(
            author_ascii,
            '[^a-z0-9 ]',
            '',
            'g'
        ) AS normalized_author

    FROM remove_subtitles

),

final_clean AS (

    SELECT

        *,

        trim(
            regexp_replace(
                normalized_title,
                '\s+',
                ' ',
                'g'
            )
        ) AS title_clean,

        trim(
            regexp_replace(
                normalized_author,
                '\s+',
                ' ',
                'g'
            )
        ) AS author_clean

    FROM normalize

)

SELECT

    kraggle_id,
    title,
    author,
    title_clean,
    author_clean,
    series_name,
    series_number,
    isbn,
    ratings_count,
    average_rating,
    text_reviews_count,
    pages,
    year_original AS year

FROM final_clean;