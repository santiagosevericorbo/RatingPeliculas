COPY book_local_file
TO 'data/books/zlib_downloads.csv'
(FORMAT CSV, HEADER, DELIMITER ',');