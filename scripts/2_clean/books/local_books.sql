DROP TABLE IF EXISTS book_local_file_clean;

CREATE TABLE book_local_file_clean AS

WITH lowered AS (

    SELECT

        id,
        file_path,
        file_name,

        lower(normalized_stem) AS s1

    FROM book_local_file

),

clean_zlib AS (

    SELECT
        *,

        regexp_replace(
            s1,
            '\(z-library\)|\(z-lib\.org\)|\(annas archive\)',
            '',
            'g'
        ) AS s2

    FROM lowered

),

clean_guion AS (

    SELECT
        *,

        replace(
            replace(
                replace(s2, '_', ' '),
                '-', ' '
            ),
            '.', ' '
        ) AS s3

    FROM clean_zlib

),

clean_spaces AS (

    SELECT
        *,

        regexp_replace(s3, '\s+', ' ', 'g') AS clean_name

    FROM clean_guion

)

SELECT

    id,
    file_path,
    file_name,

    trim(clean_name) AS clean_name

FROM clean_spaces;