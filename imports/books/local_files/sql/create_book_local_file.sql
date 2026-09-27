CREATE SEQUENCE IF NOT EXISTS book_local_file_seq;

CREATE OR REPLACE TABLE book_local_file (

    id INTEGER PRIMARY KEY DEFAULT nextval('book_local_file_seq'),

    file_path TEXT,
    file_name TEXT,

    raw_stem TEXT,
    normalized_stem TEXT,

    format TEXT,
    size_bytes BIGINT
);