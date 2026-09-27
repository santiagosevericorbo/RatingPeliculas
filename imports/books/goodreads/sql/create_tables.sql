CREATE TABLE IF NOT EXISTS my_goodreads_books_raw (
    goodreads_id     INTEGER PRIMARY KEY,
    title            VARCHAR NOT NULL,
    author           VARCHAR,
    additional_authors VARCHAR,
    isbn             VARCHAR,
    isbn13           VARCHAR,
    publisher        VARCHAR,
    binding          VARCHAR,
    pages            INTEGER,
    year_published   INTEGER,
    year_original    INTEGER
);

CREATE TABLE IF NOT EXISTS my_goodreads_books_reading (
    goodreads_id  INTEGER PRIMARY KEY REFERENCES my_goodreads_books_raw(goodreads_id),
    rating        INTEGER,         -- NULL = sin rating
    status        VARCHAR,         -- read / to-read / currently-reading
    date_read     DATE,
    date_added    DATE,
    shelves       VARCHAR,         -- custom shelves solamente
    read_count    INTEGER,
    review        VARCHAR
);
