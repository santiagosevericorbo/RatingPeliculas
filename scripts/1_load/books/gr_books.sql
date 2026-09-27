-- 1. Borramos la tabla si ya existe para empezar limpios
DROP TABLE IF EXISTS goodreads_books_raw;

CREATE TABLE goodreads_books_raw AS
SELECT *
FROM read_csv_auto(
    'data/books/goodreads/books.csv',
    header=true,
    sample_size=-1,
    ignore_errors=true
);