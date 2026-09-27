DROP TABLE IF EXISTS goodreads_activity_clean;

CREATE TABLE goodreads_activity_clean AS

WITH base AS (

    SELECT

        "Book Id" AS goodreads_id,

        "Title"  AS title,
        "Author" AS author,

        lower("Title")  AS title_lc,
        lower("Author") AS author_lc,

        "Exclusive Shelf" AS activity,
        "Binding"         AS binding,
        "ISBN13"          AS isbn,
        "Number of Pages" AS pages,

        try_cast(
            "Original Publication Year" AS INTEGER
        ) AS year

    FROM goodreads_activity_raw

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
        regexp_extract(
            title_ascii,
            '\((?:[^)]+)\s*#([0-9]+(?:[.][0-9]+)?)\)',
            1
        ) AS series_number_paren,

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
            nullif(series_number_inline, '')
        ) AS series_number

    FROM extract_series

),

remove_series_info AS (

    SELECT

        *,

        regexp_replace(
            regexp_replace(
                title_ascii,
                '\s*\([^)]*#\d+[^)]*\)',
                ''
            ),
            '\s*,?\s*(?:vol(?:ume)?[.]?|book|part)\s*[0-9]+',
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

    goodreads_id,
    title,
    author,
    title_clean,
    author_clean,
    series_name,
    series_number,
    activity,
    binding,
    isbn,
    pages,
    year

FROM final_clean;