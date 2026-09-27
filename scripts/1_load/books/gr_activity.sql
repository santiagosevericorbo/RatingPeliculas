-- 1. Borramos la tabla si ya existe para empezar limpios
DROP TABLE IF EXISTS goodreads_activity_raw;

CREATE TABLE goodreads_activity_raw AS
SELECT *
FROM read_csv(
    'data/books/goodreads/user/goodreads_library_export.csv',
    delim=',',
    quote='"',
    escape='"',
    header=true,
    all_varchar=true,
    ignore_errors=true,
    null_padding=true,
    sample_size=-1
);