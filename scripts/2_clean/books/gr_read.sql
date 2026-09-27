-- 1. Borramos la tabla si ya existe para empezar limpios
DROP TABLE IF EXISTS goodreads_activity_read_clean;

CREATE TABLE goodreads_activity_read_clean AS
SELECT *
FROM goodreads_activity_clean
WHERE activity = 'read';