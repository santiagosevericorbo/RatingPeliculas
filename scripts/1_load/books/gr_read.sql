-- 1. Borramos la tabla si ya existe para empezar limpios
DROP TABLE IF EXISTS goodreads_activity_read_raw;

CREATE TABLE goodreads_activity_read_raw AS
SELECT *
FROM goodreads_activity_raw
WHERE "Exclusive Shelf" = 'read';