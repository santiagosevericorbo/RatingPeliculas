CREATE TABLE books_resolved AS
SELECT
    b.*,

    COALESCE(
        a.canonical_title,
        b.title_clean
    ) AS canonical_title

FROM books_clean b
LEFT JOIN book_aliases a
    ON b.title_clean = a.alias_title;