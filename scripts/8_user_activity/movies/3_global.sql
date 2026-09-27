DROP TABLE IF EXISTS global_user_activity;

CREATE TABLE global_user_activity AS
SELECT * FROM imdb_user_activity

UNION ALL

SELECT * FROM letterboxd_user_activity;