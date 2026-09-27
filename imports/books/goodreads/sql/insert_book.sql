INSERT INTO my_goodreads_books_raw
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT (goodreads_id)
DO UPDATE SET
    title              = EXCLUDED.title,
    author             = EXCLUDED.author,
    additional_authors = EXCLUDED.additional_authors,
    isbn               = EXCLUDED.isbn,
    isbn13             = EXCLUDED.isbn13,
    publisher          = EXCLUDED.publisher,
    binding            = EXCLUDED.binding,
    pages              = EXCLUDED.pages,
    year_published     = EXCLUDED.year_published,
    year_original      = EXCLUDED.year_original;
