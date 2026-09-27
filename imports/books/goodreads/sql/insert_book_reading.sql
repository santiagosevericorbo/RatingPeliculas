INSERT INTO my_goodreads_books_reading
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT (goodreads_id)
DO UPDATE SET
    rating     = EXCLUDED.rating,
    status     = EXCLUDED.status,
    date_read  = EXCLUDED.date_read,
    date_added = EXCLUDED.date_added,
    shelves    = EXCLUDED.shelves,
    read_count = EXCLUDED.read_count,
    review     = EXCLUDED.review;
