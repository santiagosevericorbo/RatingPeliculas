-- 1. Borramos la tabla si ya existe para empezar limpios
DROP TABLE IF EXISTS goodreads_activity_readList_clean;

CREATE TABLE goodreads_activity_readList_clean AS
SELECT *
FROM goodreads_activity_clean
WHERE activity = 'to-read';